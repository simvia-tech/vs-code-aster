import sys
import traceback

from command_core import CommandCore
from lsprotocol.types import (
    Command,
    CompletionItem,
    CompletionItemKind,
    CompletionList,
    InsertTextFormat,
    MarkupContent,
    MarkupKind,
)


def _retrigger_command() -> Command:
    """A `Command` that asks VS Code to re-open the suggestion popup right
    after the snippet finishes inserting. Used so accepting `LIRE_MAILLAGE`
    immediately offers its keyword args, and accepting `FORMAT=` immediately
    offers its allowed values."""
    return Command(title="Trigger suggest", command="editor.action.triggerSuggest")


def _log(msg: str) -> None:
    """Write to stderr so the line surfaces in the LSP's Output channel
    (Python Language Server), same place the [catalog] lines land."""
    sys.stderr.write(msg + "\n")
    sys.stderr.flush()


class CompletionManager:
    """Auto-completion for code_aster `.comm` files.

    Dispatches one of four behaviors based on the cursor context:
      * outside any command call → list of all catalog commands
      * inside `KEY=` (value position) → allowed-value literals (`into`)
      * inside a `_F(...)` factor frame → that factor's sub-keywords
      * otherwise inside a call → remaining top-level keywords

    All dispatch decisions come from a single forward scan over the document
    bytes between the enclosing command's opening `(` and the cursor. Forward
    scanning (rather than backwards) makes mid-edit unmatched quotes / parens
    a non-issue: strings open and close left-to-right.
    """

    def __init__(self):
        self.core = CommandCore()

    # ---------------------------------------------------------------- entry

    def completion(self, doc_uri: str, position) -> CompletionList:
        try:
            return self._completion(doc_uri, position)
        except Exception as exc:
            _log("[completion] ERROR: " + repr(exc) + "\n" + traceback.format_exc())
            return CompletionList(is_incomplete=False, items=[])

    def _completion(self, doc_uri: str, position) -> CompletionList:
        registry = self.core.get_registry(doc_uri)
        doc = self.core.get_doc_from_uri(doc_uri)
        if registry is None or doc is None:
            _log(
                f"[completion] line={position.line} col={position.character} "
                f"registry={registry is not None} doc={doc is not None} → empty"
            )
            return CompletionList(is_incomplete=True, items=[])

        cmd_info = registry.get_command_at_line(position.line + 1)
        if not cmd_info:
            result = self._suggest_commands()
            _log(
                f"[completion] line={position.line} col={position.character} "
                f"cmd=None registry_size={len(registry.commands)} "
                f"ranges={registry.ranges} items={len(result.items)} kind=Function"
            )
            return result

        cmd_def = self.core.get_command_def(cmd_info.name)
        if not cmd_def or "params" not in cmd_def:
            _log(f"[completion] cmd={cmd_info.name} but parse_command returned no params → empty")
            return CompletionList(is_incomplete=True, items=[])

        scan = _scan_forward(doc.lines, cmd_info, position)

        # Descend into the factor path to scope the visible parameters.
        params_list = cmd_def["params"]
        for factor_name in scan.factor_path:
            entry = _find_param(params_list, factor_name)
            if not entry or not entry["children"]:
                break
            params_list = entry["children"]

        # Value position takes precedence over keyword listing.
        if scan.value_keyword is not None:
            target = _find_param(params_list, scan.value_keyword)
            items: list[CompletionItem] = []
            if target is not None:
                remaining = _remaining_keyword_count(
                    params_list, scan.written_keys | {scan.value_keyword}
                )
                more = remaining > 0
                if target.get("allowed"):
                    items.extend(_value_items(target, scan.inside_quotes, append_comma=more))
                items.extend(
                    _variable_items(registry, self.core, target, position, append_comma=more)
                )
            _log(
                f"[completion] cmd={cmd_info.name} factor_path={scan.factor_path} "
                f"value_keyword={scan.value_keyword} inside_quotes={scan.inside_quotes} "
                f"items={len(items)} kind=Value"
            )
            return CompletionList(is_incomplete=True, items=items)

        # Keyword-arg list at the current scope. The forward scan tracks
        # `written_keys` per scope, so the factor branch is now able to
        # filter already-typed sub-keywords too.
        written = set(scan.written_keys)
        if not scan.factor_path:
            # At the top level, also include the registry's parsed_params
            # (which were tracked at didOpen / didChange time and may
            # cover params written in earlier sessions of this call).
            written |= set(cmd_info.parsed_params.keys())
            context = cmd_info.parsed_params.copy()
        else:
            context = None

        result = self._suggest_parameters(params_list, written, context)
        _log(
            f"[completion] cmd={cmd_info.name} factor_path={scan.factor_path} "
            f"value_keyword=None inside_quotes={scan.inside_quotes} "
            f"written={sorted(written)} "
            f"available={[p['name'] for p in params_list if not p.get('bloc')]} "
            f"items={len(result.items)} kind=Property"
        )
        return result

    # ----------------------------------------------- top-level command list

    def _suggest_commands(self) -> CompletionList:
        items = []
        for cmd in self.core.get_CATA_commands():
            items.append(
                CompletionItem(
                    label=cmd["name"],
                    kind=CompletionItemKind.Function,
                    insert_text=cmd["name"] + "($0)",
                    insert_text_format=InsertTextFormat.Snippet,
                    command=_retrigger_command(),
                    documentation=_md(cmd.get("doc", "")),
                )
            )
        return CompletionList(is_incomplete=False, items=items)

    # -------------------------------------------------- keyword suggestions

    def _suggest_parameters(self, params_list, written, context) -> CompletionList:
        visible = self._expand_condition_bloc(params_list, context)
        items = []
        for param in visible:
            name = param["name"]
            if name in written:
                continue
            if param.get("bloc") is not None:
                if context is None:
                    for child in param["children"]:
                        if child["name"] not in written:
                            items.append(_keyword_item(child))
                continue
            items.append(_keyword_item(param))
        return CompletionList(is_incomplete=False, items=items)

    # _suggest_values is split into module-level helpers (_value_items,
    # _variable_items) so the value-position branch can combine sources
    # without re-instantiating CompletionList multiple times.

    def _expand_condition_bloc(self, params, context):
        if context is None:
            return params
        out = []
        for arg in params:
            if arg.get("bloc"):
                if arg["bloc"].isEnabled(context):
                    out.extend(arg["children"])
            else:
                out.append(arg)
        return out


# ===================== helpers ============================================


def _find_param(params, name):
    for p in params:
        if p.get("name") == name:
            return p
        if p.get("bloc"):
            inner = _find_param(p.get("children", []), name)
            if inner:
                return inner
    return None


def _md(text: str) -> MarkupContent | None:
    text = (text or "").strip()
    if not text:
        return None
    return MarkupContent(kind=MarkupKind.Markdown, value=text)


def _detail(param) -> str | None:
    bits = []
    typ = param.get("type")
    if typ:
        bits.append(typ)
    default = param.get("default")
    if default is not None:
        if isinstance(default, str):
            bits.append(f'= "{default}"')
        else:
            bits.append(f"= {default}")
    if param.get("required"):
        bits.append("required")
    return " · ".join(bits) if bits else None


def _doc_md(param) -> MarkupContent | None:
    parts = []
    doc = (param.get("doc") or "").strip()
    if doc:
        parts.append(f"*{doc}*")
    allowed = param.get("allowed")
    if allowed:
        rendered = " | ".join(f'"{v}"' if isinstance(v, str) else str(v) for v in allowed)
        parts.append(f"**Allowed:** {rendered}")
    if not parts:
        return None
    return MarkupContent(kind=MarkupKind.Markdown, value="\n\n".join(parts))


def _remaining_keyword_count(params_list, used_keys) -> int:
    """How many SIMP/FACT keywords would still be valid choices once the
    `used_keys` set has been written. Counts BLOC children too — without a
    context to filter them we just assume any could become available."""
    count = 0
    for p in params_list:
        if p.get("bloc") is not None:
            for child in p.get("children", []):
                if child["name"] not in used_keys:
                    count += 1
        elif p["name"] not in used_keys:
            count += 1
    return count


def _value_items(param, inside_quotes: bool, append_comma: bool = True) -> list[CompletionItem]:
    suffix = ", " if (append_comma and not inside_quotes) else ""
    out = []
    for v in param["allowed"]:
        if isinstance(v, str):
            if inside_quotes:
                insert = v
            else:
                insert = f"'{v}'{suffix}"
            label = f"'{v}'"
        else:
            insert = f"{v}{suffix}"
            label = str(v)
        out.append(
            CompletionItem(
                label=label,
                kind=CompletionItemKind.Value,
                insert_text=insert,
                command=None if inside_quotes or not suffix else _retrigger_command(),
                detail=param.get("type") or None,
            )
        )
    return out


def _command_return_types(cmd_obj) -> tuple:
    """Resolve a command's `sd_prod` to a tuple of concrete output classes.

    `sd_prod` may be (a) a class, (b) a callable that returns a class or
    tuple of classes when invoked with `__all__=True` (the convention
    used in code_aster catalogs — see e.g. `lire_maillage_sdprod` which
    returns `(maillage_sdaster, maillage_p)`), or (c) None. Callable form
    typically requires positional args (like `FORMAT, PARTITIONNEUR`) so
    we introspect the signature and pad the call with `None`s before
    setting `__all__=True`.
    """
    sd = cmd_obj.definition.get("sd_prod") if hasattr(cmd_obj, "definition") else None
    if sd is None:
        return ()
    if isinstance(sd, type):
        return (sd,)
    if not callable(sd):
        return ()

    import inspect

    try:
        sig = inspect.signature(sd)
        positional = [
            p
            for p in sig.parameters.values()
            if p.kind == inspect.Parameter.POSITIONAL_OR_KEYWORD
            and p.default is inspect.Parameter.empty
        ]
        result = sd(*([None] * len(positional)), __all__=True)
    except Exception:
        return ()
    if isinstance(result, type):
        return (result,)
    if isinstance(result, (tuple, list)):
        return tuple(t for t in result if isinstance(t, type))
    return ()


def _expected_classes(param) -> tuple:
    """Pull the raw type(s) the SIMP keyword expects."""
    typ = param.get("type_obj")
    if typ is None:
        return ()
    if isinstance(typ, type):
        return (typ,)
    if isinstance(typ, (tuple, list)):
        return tuple(t for t in typ if isinstance(t, type))
    return ()


def _types_compatible(var_types, expected) -> bool:
    if not var_types or not expected:
        return False
    for vt in var_types:
        for et in expected:
            try:
                if issubclass(vt, et):
                    return True
            except TypeError:
                continue
    return False


def _variable_items(
    registry, core, param, position, append_comma: bool = True
) -> list[CompletionItem]:
    """Suggest already-declared variables whose type is compatible with
    the SIMP keyword the cursor is filling in."""
    expected = _expected_classes(param)
    if not expected:
        return []
    cursor_line_1based = position.line + 1
    out: list[CompletionItem] = []
    seen: set[str] = set()
    cata = core.get_CATA()
    # Iterate in the registry's natural order so we can list earliest
    # assignments first, but skip duplicates (var reassigned later).
    for cmd_info in sorted(registry.commands.values(), key=lambda c: c.start_line):
        var = getattr(cmd_info, "var_name", None)
        if not var or var in seen:
            continue
        # Don't suggest a variable whose assignment is below the cursor.
        if cmd_info.start_line >= cursor_line_1based:
            continue
        cmd_obj = cata.get_command_obj(cmd_info.name)
        if cmd_obj is None:
            continue
        var_types = _command_return_types(cmd_obj)
        if not _types_compatible(var_types, expected):
            continue
        seen.add(var)
        type_name = ", ".join(t.__name__ for t in var_types) or "?"
        suffix = ", " if append_comma else ""
        out.append(
            CompletionItem(
                label=var,
                kind=CompletionItemKind.Variable,
                insert_text=f"{var}{suffix}",
                insert_text_format=InsertTextFormat.PlainText,
                command=_retrigger_command() if suffix else None,
                detail=f"{type_name} (line {cmd_info.start_line})",
                documentation=_md(f"Assigned by `{cmd_info.name}` at line {cmd_info.start_line}."),
            )
        )
    return out


def _keyword_item(param) -> CompletionItem:
    name = param["name"]
    is_factor = bool(param["children"]) and not param.get("bloc")
    if is_factor:
        insert = f"{name}=_F($0)"
    else:
        # `$0` after `=` lets VS Code know to leave the cursor right after
        # the `=`; combined with the trigger-suggest command below, the
        # value popup opens automatically when the param has `into=(...)`.
        insert = f"{name}=$0"
    return CompletionItem(
        label=name,
        kind=CompletionItemKind.Property,
        insert_text=insert,
        insert_text_format=InsertTextFormat.Snippet,
        command=_retrigger_command(),
        detail=_detail(param),
        documentation=_doc_md(param),
    )


# ----------------- forward cursor-context scan ----------------------------


_IDENT_CHARS = frozenset("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_")


class _Scan:
    """Result of the forward scan."""

    __slots__ = ("factor_path", "value_keyword", "inside_quotes", "written_keys")

    def __init__(self):
        self.factor_path: list[str] = []  # outer → inner, excluding the command itself
        self.value_keyword: str | None = None
        self.inside_quotes: bool = False
        # Names of kwargs already written at the cursor's current scope —
        # used to filter the keyword popup so we don't suggest a kwarg the
        # user has already filled in (works inside _F(...) too, where the
        # registry's parsed_params doesn't reach).
        self.written_keys: set[str] = set()


def _scan_forward(doc_lines, cmd_info, position) -> _Scan:
    """Walk forward from `cmd_info.start_line` to the cursor, classifying
    where we are. Strings open/close monotonically, paren depth ditto."""
    cursor_line = position.line  # 0-based
    cursor_col = position.character
    start_idx = max(0, cmd_info.start_line - 1)

    # Stack frames are (name, depth_at_open). depth_at_open is the depth
    # right BEFORE the open paren (so the matching close pops when depth
    # falls back to it).
    stack: list[tuple[str, int]] = []
    # `seen_stack[i]` holds the set of kwarg names already typed at the
    # depth of `stack[i]`. The top of the stack is always the cursor's
    # current scope; we additionally maintain `seen_top` for the cursor's
    # outermost scope (top-level call) when no factor is open.
    seen_stack: list[set[str]] = [set()]
    depth = 0
    in_string: str | None = None
    # `last_kw` is the last identifier seen at the current scope that was
    # immediately followed by `=`. Reset on commas, closing parens, or any
    # significant non-whitespace token after the `=` is consumed.
    last_kw: str | None = None
    # `value_pos` is True when we've seen `KEY=` and not yet seen any
    # significant token (anything other than whitespace or an opening quote).
    value_pos: bool = False
    # Identifier accumulator for parsing names left-to-right.
    pending_name: str | None = None

    for line_idx in range(start_idx, cursor_line + 1):
        if line_idx >= len(doc_lines):
            break
        line = doc_lines[line_idx]
        col_end = cursor_col if line_idx == cursor_line else len(line)
        i = 0
        while i < col_end:
            c = line[i]

            if in_string:
                # Consume the string body. Closing quote terminates.
                if c == in_string and (i == 0 or line[i - 1] != "\\"):
                    in_string = None
                    # Exiting a string is a "significant token" — clear
                    # value_pos so a later `KEY=` is required to reactivate.
                    value_pos = False
                    last_kw = None
                i += 1
                continue

            if c in ("'", '"'):
                # Opening a string. If we were in value_pos, we stay there
                # so the cursor inside the string still resolves to
                # value_keyword=last_kw.
                in_string = c
                i += 1
                continue

            # Outside a string. Identifier accumulation.
            if c in _IDENT_CHARS:
                if pending_name is None:
                    pending_name = c
                else:
                    pending_name += c
                i += 1
                continue
            else:
                # Non-identifier: see if pending_name + this char is `NAME=`
                # (kwarg) or `NAME(` (call). If `=`, mark value_pos. If `(`,
                # push a stack frame. Otherwise just discard pending_name.
                # Skip whitespace inline first.
                if c.isspace():
                    if pending_name is not None:
                        # finalize: still pending; allow whitespace then `=`/`(`
                        pass
                    i += 1
                    continue

                if c == "=":
                    # `KEY=` is a kwarg only when we're inside a call (depth>0).
                    # At depth 0 it's a Python statement assignment (`VAR =
                    # CMD(...)`) and the LHS should not be treated as a
                    # keyword name.
                    if (
                        depth > 0
                        and pending_name is not None
                        and (i + 1 >= len(line) or line[i + 1] != "=")
                    ):
                        last_kw = pending_name
                        value_pos = True
                        # Mark this key as already-written in the current
                        # scope (top of seen_stack, parallel to call stack).
                        seen_stack[-1].add(pending_name)
                        pending_name = None
                    else:
                        pending_name = None
                        value_pos = False
                        last_kw = None
                    i += 1
                    continue

                if c == "(":
                    # `KEY=_F(...)` — the factor's identity in the catalog
                    # is KEY, not the literal `_F`. Push the kwarg name so
                    # the descent in `params_list` resolves correctly.
                    if value_pos and last_kw is not None:
                        stack.append((last_kw, depth))
                    elif pending_name is not None:
                        stack.append((pending_name, depth))
                    pending_name = None
                    depth += 1
                    seen_stack.append(set())
                    value_pos = False
                    last_kw = None
                    i += 1
                    continue

                if c == ")":
                    depth -= 1
                    while stack and stack[-1][1] >= depth:
                        stack.pop()
                    if len(seen_stack) > 1:
                        seen_stack.pop()
                    pending_name = None
                    value_pos = False
                    last_kw = None
                    i += 1
                    continue

                if c == ",":
                    pending_name = None
                    value_pos = False
                    last_kw = None
                    i += 1
                    continue

                if c == "#":
                    # Comment runs to end of line.
                    break

                # Any other char (digits, dots, operators, etc.) — clears
                # the identifier accumulator but NOT the value-position
                # state. The user typing `APLAT=0.5` is still in
                # APLAT's value scope until a `,` or `)`.
                pending_name = None
                i += 1

        # End of this line slice. If we end inside a string, that's part of
        # the cursor's state we need to remember.

    out = _Scan()
    out.inside_quotes = in_string is not None
    if value_pos and last_kw is not None:
        out.value_keyword = last_kw
    # Drop the outer command frame from the stack to get the factor path.
    factor_frames = stack[:]
    if factor_frames and factor_frames[0][0] == cmd_info.name:
        factor_frames = factor_frames[1:]
    out.factor_path = [name for name, _d in factor_frames]
    # The current scope's already-written kwargs (top of seen_stack).
    out.written_keys = set(seen_stack[-1]) if seen_stack else set()
    return out
