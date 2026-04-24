"""
HoverManager — TypeScript-style hovers for code_aster commands.

Everything interesting lives in a fenced ```python block so VS Code applies
the active theme's syntax highlighting (keywords, strings, numbers,
identifiers all get their theme colors). Supplementary text is kept as
short Markdown below the fence.

Three cases, in order of preference:
  1. cursor on a command name   → full signature of that command
  2. cursor inside a command, on one of its keywords → single-keyword detail
  3. cursor on any known command name elsewhere → full signature, no context
"""

import os
import re

from command_core import CommandCore
from lsprotocol.types import Hover, MarkupContent, MarkupKind

try:
    from asterstudy.datamodel.dict_categories import DEPRECATED as _DEPRECATED_LIST
except Exception:
    _DEPRECATED_LIST = []
_DEPRECATED = set(_DEPRECATED_LIST)


# Currently the Simvia doc site only hosts `v17`. Once more versions are
# published, switch back to deriving the major from `CATA.version_number`.
DOC_BASE_URL = "https://demo-docaster.simvia-app.fr/versions/v17/search.html?q={name}"


def _lang() -> str:
    """Very light locale detection: returns 'fr' if the environment suggests
    French, 'en' otherwise. VS Code forwards LANG/LC_ALL to the LSP process
    (see `vs-code-aster.pythonExecutablePath` spawn env), so this is enough
    to pick a UI-language without wiring LSP `initialize.locale` through
    pygls."""
    for var in ("VSCODE_NLS_CONFIG", "LC_ALL", "LC_MESSAGES", "LANG"):
        v = os.environ.get(var, "")
        if not v:
            continue
        if v.lower().startswith("fr") or '"locale":"fr' in v.lower():
            return "fr"
        if v.lower().startswith("en") or '"locale":"en' in v.lower():
            return "en"
    return "en"


_I18N = {
    "search_doc": {
        "en": "Search documentation for `{name}`",
        "fr": "Rechercher la documentation de `{name}`",
    },
    "rules": {"en": "Rules", "fr": "Règles"},
    "status": {"en": "Status", "fr": "Statut"},
    "required": {"en": "required", "fr": "obligatoire"},
    "optional": {"en": "optional", "fr": "facultatif"},
    "optional_defaulted": {"en": "optional (defaulted)", "fr": "facultatif (par défaut)"},
    "cached": {"en": "cached", "fr": "en cache"},
    "allowed_values": {"en": "Allowed values", "fr": "Valeurs permises"},
    "range": {"en": "Range", "fr": "Plage"},
    "assigned_by": {
        "en": "Assigned by `{cmd}` at line {line}",
        "fr": "Assigné par `{cmd}` à la ligne {line}",
    },
    "assigned_at_line": {
        "en": "Assigned at line {line}",
        "fr": "Assigné à la ligne {line}",
    },
    "allowed_value": {
        "en": "Allowed value for `{parent}.{kw}`",
        "fr": "Valeur permise pour `{parent}.{kw}`",
    },
    "factor_marker_desc": {
        "en": "Factor keyword block — groups related sub-keywords as a single record.",
        "fr": "Mot-clé facteur — regroupe des sous-mots-clés liés en un seul bloc.",
    },
    "legacy": {
        "en": "Legacy command — still supported.",
        "fr": "Commande héritée — toujours supportée.",
    },
}


def _t(key: str, **kwargs) -> str:
    entry = _I18N.get(key, {})
    return entry.get(_lang(), entry.get("en", key)).format(**kwargs)


def _udocstring(obj, key: str | None = None, translation: dict | None = None) -> str:
    """Pick the best-available docstring, in order:
    1. the command-scoped `translation={...}` dict, if a matching entry exists
       (this is how code_aster catalogs expose English short labels for
       command names AND their keywords);
    2. the DSL's `ang=` argument, if declared;
    3. the default `fr=` docstring (exposed via `udocstring`).
    """
    if translation and key and key in translation:
        v = translation[key]
        if v:
            return str(v).strip()
    try:
        ang = obj.definition.get("ang") if hasattr(obj, "definition") else None
    except Exception:
        ang = None
    if ang:
        return str(ang).strip()
    return (getattr(obj, "udocstring", "") or "").strip()


def _translation_of(cmd_obj) -> dict:
    try:
        return cmd_obj.definition.get("translation") or {}
    except Exception:
        return {}


_RULE_LABELS = {
    "AtLeastOne": "At least one of: {args}",
    "ExactlyOne": "Exactly one of: {args}",
    "AtMostOne": "At most one of: {args}",
    "IfFirstAllPresent": "If `{first}` is set, all of these must also be set: {rest}",
    "OnlyFirstPresent": "If `{first}` is set, none of these may be set: {rest}",
    "AllTogether": "Either all or none of: {args}",
    "NotEmpty": "At least one keyword must be provided",
    "AtMostOneStartsWith": "At most one keyword starting with: {args}",
}


def _rules_to_bullets(rules) -> list[str]:
    bullets: list[str] = []
    for rule in rules or []:
        cls = type(rule).__name__
        args = getattr(rule, "ruleArgs", ()) or ()
        joined = ", ".join(f"`{a}`" for a in args) if args else ""
        first = f"`{args[0]}`" if args else ""
        rest = ", ".join(f"`{a}`" for a in args[1:]) if len(args) > 1 else ""
        template = _RULE_LABELS.get(cls, f"{cls}({{args}})")
        try:
            bullets.append(template.format(args=joined, first=first, rest=rest))
        except Exception:
            bullets.append(f"{cls}: {joined}")
    return bullets


def _doc_url(name: str) -> str | None:
    return DOC_BASE_URL.format(name=name)


class HoverManager:
    def __init__(self):
        self.core = CommandCore()

    def display(self, doc_uri, position):
        doc = self.core.get_doc_from_uri(doc_uri)
        if doc is None or position.line >= len(doc.lines):
            return None
        line_text = doc.lines[position.line]
        word = _word_at(line_text, position.character)
        if not word:
            return None

        registry = self.core.get_registry(doc_uri)
        cmd_info = registry.get_command_at_line(position.line + 1) if registry else None
        context = cmd_info.parsed_params if cmd_info else None
        cata = self.core.get_CATA()

        # (3) `_F` factor marker — standalone card; cheap check first.
        if word == "_F":
            return _hover(_render_factor_marker())

        if cmd_info and word == cmd_info.name:
            cmd_obj = cata.get_command_obj(word)
            return _hover(_render_command(cmd_obj, context)) if cmd_obj else None

        if cmd_info:
            cmd_obj = cata.get_command_obj(cmd_info.name)
            if cmd_obj is not None:
                # (2) Allowed-value literal: cursor is on a word inside a
                # `KEY=<value>` assignment within this command call. Only fire
                # when the word is actually listed in the keyword's `into`.
                kw_name = _enclosing_keyword_name(line_text, position.character)
                if kw_name:
                    target = _find_keyword(cmd_obj.definition, kw_name, context)
                    if target is not None:
                        into = target.definition.get("into") or ()
                        if _matches_into_value(word, into):
                            return _hover(_render_allowed_value(word, kw_name, cmd_obj))

                kwd = _find_keyword(cmd_obj.definition, word, context)
                if kwd is not None:
                    return _hover(_render_keyword(word, kwd, cmd_obj))

        cmd_obj = cata.get_command_obj(word)
        if cmd_obj is not None:
            return _hover(_render_command(cmd_obj, context=None))

        # (1) Variable reference: match against the nearest preceding
        # assignment whose `var_name` equals `word`. This fires last so a
        # command name hover (e.g. `LIRE_MAILLAGE`) still wins if somehow
        # reused as a variable.
        if registry is not None:
            assignment = _nearest_assignment(registry, word, position.line + 1)
            if assignment is not None:
                return _hover(_render_variable_reference(word, assignment, cata))

        # (1b) Plain Python assignments (e.g. `TempRef = 20.0`) aren't
        # tracked by CommandRegistry. Scan the doc for the nearest preceding
        # line-level `WORD = <rhs>` and infer a simple Python type.
        literal = _nearest_literal_assignment(doc.lines, word, position.line)
        if literal is not None:
            line_no, rhs = literal
            return _hover(_render_literal_assignment(word, rhs, line_no))
        return None


def _hover(markdown: str):
    if not markdown:
        return None
    return Hover(contents=MarkupContent(kind=MarkupKind.Markdown, value=markdown))


def _escape_italic(text: str) -> str:
    """Stop `*` inside the docstring from closing our italic wrap."""
    return text.replace("*", "\\*")


# ---------- variable-reference helper -------------------------------------


def _nearest_assignment(registry, var_name: str, cursor_line: int):
    """Walk all tracked commands; return the CommandInfo whose `var_name`
    matches and whose assignment line is on or before the cursor. Prefers
    the most recent prior assignment."""
    best = None
    for info in registry.commands.values():
        if getattr(info, "var_name", None) != var_name:
            continue
        if info.start_line > cursor_line:
            continue
        if best is None or info.start_line > best.start_line:
            best = info
    return best


def _render_variable_reference(name: str, info, cata) -> str:
    cmd_obj = cata.get_command_obj(info.name) if info.name else None
    type_str = _return_type_hint(cmd_obj) if cmd_obj else None
    header = f"{name}: {type_str}" if type_str else name

    out: list[str] = []
    out.append("```python")
    out.append(header)
    out.append("```")
    out.append("")
    out.append("*" + _escape_italic(_t("assigned_by", cmd=info.name, line=info.start_line)) + "*")
    # Footer still points at the command that produced it.
    if info.name:
        _append_doc_link(out, info.name)
    return "\n".join(out) + "\n"


# ---------- plain-literal assignment helpers ------------------------------

_LITERAL_ASSIGN_RE = re.compile(r"^\s*([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.+?)\s*$")


def _nearest_literal_assignment(lines, word: str, cursor_line_0: int):
    """Walk the doc backwards from the cursor; return `(line_1based, rhs)`
    of the nearest assignment `word = rhs` whose RHS is NOT a call of the
    form `COMMAND(...)` (those are handled by CommandRegistry)."""
    end = min(cursor_line_0, len(lines) - 1)
    for i in range(end, -1, -1):
        line = lines[i]
        m = _LITERAL_ASSIGN_RE.match(line)
        if not m:
            continue
        if m.group(1) != word:
            continue
        rhs = m.group(2)
        # Skip assignments that are LIRE_MAILLAGE(…)-style — handled above.
        if re.match(r"^[A-Z_][A-Z0-9_]*\s*\(", rhs):
            continue
        # Skip the line where the cursor is, since that's a definition not
        # a reference — unless the hover is on the LHS we want to describe
        # the value anyway; return it.
        return i + 1, rhs
    return None


def _infer_literal_type(rhs: str) -> str | None:
    rhs = rhs.strip().rstrip(",").strip()
    if not rhs:
        return None
    if rhs in ("None",):
        return "None"
    if rhs in ("True", "False"):
        return "bool"
    if rhs[0] in ('"', "'"):
        return "str"
    if rhs.startswith("("):
        return "tuple"
    if rhs.startswith("["):
        return "list"
    if rhs.startswith("{"):
        return "dict"
    if re.match(r"^-?\d+$", rhs):
        return "int"
    if (
        re.match(r"^-?\d+\.\d*([eE][+-]?\d+)?$", rhs)
        or re.match(r"^-?\d*\.\d+([eE][+-]?\d+)?$", rhs)
        or re.match(r"^-?\d+[eE][+-]?\d+$", rhs)
    ):
        return "float"
    return None


def _render_literal_assignment(name: str, rhs: str, line_no: int) -> str:
    type_str = _infer_literal_type(rhs)
    # Show the actual RHS as the "value" so the hover is instantly useful
    # even when type inference falls short.
    rhs_display = rhs if len(rhs) <= 80 else rhs[:77] + "..."
    out: list[str] = []
    out.append("```python")
    if type_str:
        out.append(f"{name}: {type_str} = {rhs_display}")
    else:
        out.append(f"{name} = {rhs_display}")
    out.append("```")
    out.append("")
    out.append("*" + _escape_italic(_t("assigned_at_line", line=line_no)) + "*")
    return "\n".join(out) + "\n"


# ---------- allowed-value helper ------------------------------------------

# Finds the last `KEY=` on the line before the cursor, tolerating quoted or
# unquoted values. The keyword name is the last CAPS-ish identifier that was
# an LHS of `=`.
_KW_ASSIGN_RE = re.compile(r"\b([A-Z_][A-Z0-9_]*)\s*=\s*['\"]?")


def _enclosing_keyword_name(line: str, char_pos: int) -> str | None:
    m = None
    for candidate in _KW_ASSIGN_RE.finditer(line):
        if candidate.end() > char_pos:
            break
        m = candidate
    return m.group(1) if m else None


def _matches_into_value(word: str, into) -> bool:
    try:
        for v in into:
            if isinstance(v, str) and v == word:
                return True
            if isinstance(v, (int, float)) and str(v) == word:
                return True
    except Exception:
        pass
    return False


def _render_allowed_value(value: str, kw_name: str, cmd_obj) -> str:
    translation = _translation_of(cmd_obj)
    parent_name = cmd_obj.name

    out: list[str] = []
    out.append("```python")
    # Show as a value assignment so the theme's string/number color applies.
    # Strings are quoted; integers/floats render bare.
    out.append(f"{kw_name} = {_format_value(value)}")
    out.append("```")
    out.append("")
    out.append("*" + _escape_italic(_t("allowed_value", parent=parent_name, kw=kw_name)) + "*")

    # If the keyword has a docstring / label, include it for extra context.
    kwd = _find_keyword(cmd_obj.definition, kw_name, context=None)
    if kwd is not None:
        doc = _udocstring(kwd, key=kw_name, translation=translation)
        if doc:
            out.append("")
            out.append(f"*{_escape_italic(doc)}*")

    _append_doc_link(out, parent_name)
    return "\n".join(out) + "\n"


# ---------- _F marker helper ----------------------------------------------


def _render_factor_marker() -> str:
    out: list[str] = []
    out.append("```python")
    out.append("_F(...)")
    out.append("```")
    out.append("")
    out.append(f"*{_escape_italic(_t('factor_marker_desc'))}*")
    return "\n".join(out) + "\n"


def _word_at(line: str, char_pos: int) -> str:
    for m in re.finditer(r"\b\w+\b", line):
        if m.start() <= char_pos <= m.end():
            return m.group()
    return ""


def _is_factor(kwd) -> bool:
    return "FactorKeyword" in type(kwd).__name__


def _is_bloc(kwd) -> bool:
    return "Bloc" in type(kwd).__name__


def _format_type(typ) -> str:
    if isinstance(typ, str):
        return {"R": "float", "I": "int", "TXM": "str", "C": "complex"}.get(typ, typ)
    if isinstance(typ, type):
        return typ.__name__
    if isinstance(typ, (tuple, list)) and typ and all(isinstance(t, type) for t in typ):
        return " | ".join(t.__name__ for t in typ)
    cls = typ.__class__.__name__
    if cls == "UnitType":
        return "UnitLogique"
    return str(typ)


def _format_value(v) -> str:
    # Python-literal rendering so the theme's string / number / bool / None
    # colors apply inside a `python` fence.
    if v is None:
        return "None"
    if isinstance(v, bool):
        return "True" if v else "False"
    if isinstance(v, str):
        return '"' + v.replace('"', '\\"') + '"'
    if isinstance(v, (int, float)):
        return repr(v)
    if isinstance(v, (list, tuple)):
        return "(" + ", ".join(_format_value(x) for x in v) + ("," if len(v) == 1 else "") + ")"
    return repr(v)


def _find_keyword(definition, name: str, context):
    """Depth-first search through FACTs and BLOCs. BLOCs disabled by context
    are skipped so context-inactive keywords are not matched."""
    for key, kwd in definition.items():
        if not hasattr(kwd, "definition"):
            continue
        if _is_bloc(kwd):
            if context is not None:
                try:
                    if not kwd.isEnabled(context):
                        continue
                except Exception:
                    pass
            found = _find_keyword(kwd.definition, name, context)
            if found is not None:
                return found
            continue
        if key == name:
            return kwd
        if _is_factor(kwd):
            found = _find_keyword(kwd.definition, name, context)
            if found is not None:
                return found
    return None


def _render_command(cmd_obj, context) -> str:
    name = cmd_obj.name
    return_type = _return_type_hint(cmd_obj)
    translation = _translation_of(cmd_obj)

    doc = _udocstring(cmd_obj, key=name, translation=translation)

    signature_lines: list[str] = [f"{name}("]
    _append_signature(
        cmd_obj.definition,
        context,
        signature_lines,
        indent=1,
        factors=[],
        translation=translation,
    )
    signature_lines.append(f") → {return_type}" if return_type else ")")
    signature = "\n".join(signature_lines)

    out: list[str] = []
    # 1. Signature — the highlighted artifact the user came for.
    out.append("```python")
    out.append(signature)
    out.append("```")

    # 2. Description — italic paragraph below the signature, like TS / Rust
    # hover layouts.
    if doc:
        out.append("")
        out.append(f"*{_escape_italic(doc)}*")

    # 2b. Legacy note — some commands are marked as such in the upstream
    # catalog (DEBUT/FIN/INCLUDE/POURSUITE/DEFI_FICHIER are still required
    # but categorised as legacy/boilerplate). Small italic line, no alarm.
    if name in _DEPRECATED:
        out.append("")
        out.append(f"<sub>*{_escape_italic(_t('legacy'))}*</sub>")

    # 3. Details — rules (if any).
    rules = _rules_to_bullets(getattr(cmd_obj, "_rules", None))
    if rules:
        out.append("")
        out.append(f"**{_t('rules')}**")
        for r in rules:
            out.append(f"- {r}")

    # 4. Footer — doc link with a separator.
    _append_doc_link(out, name)
    return "\n".join(out) + "\n"


def _append_doc_link(out: list[str], command_name: str) -> None:
    """Always the last block. Preceded by a horizontal rule so it reads as a
    footer separate from the content above it."""
    url = _doc_url(command_name)
    if not url:
        return
    out.append("")
    out.append("---")
    out.append(f"[📘 {_t('search_doc', name=command_name)}]({url})")


def _return_type_hint(cmd_obj) -> str | None:
    sd_prod = cmd_obj.definition.get("sd_prod") if hasattr(cmd_obj, "definition") else None
    if sd_prod is None:
        return None
    if isinstance(sd_prod, type):
        return sd_prod.__name__
    # sd_prod may be a callable returning the type dynamically; we can't
    # safely evaluate it here, so report its name if introspectable.
    return getattr(sd_prod, "__name__", None)


def _append_signature(
    definition,
    context,
    out: list[str],
    indent: int,
    factors: list | None = None,
    translation: dict | None = None,
) -> None:
    """Render a command's keyword tree as Python-like lines inside a fence.

    - SIMP keywords become `NAME: type = default,` or `NAME: type,` if no default.
    - FACTs:
        * at the top level (factors list supplied) → rendered as a one-line
          `NAME=_F(...),` placeholder and the real body is appended to
          `factors` for later <details> rendering.
        * nested (factors=None) → expanded inline with sub-keywords indented.
    - BLOCs:
        * with a known context → flatten active branches at the same indent;
        * without a context → prefix children with `# when <condition>` so
          the fence still highlights the keyword names underneath.
    """
    pad = "    " * indent
    for key, kwd in definition.items():
        if not hasattr(kwd, "definition"):
            continue

        if _is_bloc(kwd):
            is_enabled = None
            if context is not None:
                try:
                    is_enabled = bool(kwd.isEnabled(context))
                except Exception:
                    is_enabled = None
            if is_enabled is False:
                continue
            if is_enabled is None and context is None:
                cond = _clean_condition(kwd.getCondition())
                out.append(f"{pad}# when {cond}")
            _append_signature(
                kwd.definition,
                None if is_enabled is None else context,
                out,
                indent,
                factors,
                translation,
            )
            continue

        if _is_factor(kwd):
            if factors is not None:
                out.append(f"{pad}{key}=_F(...),")
                factors.append((key, kwd))
            else:
                out.append(f"{pad}{key}=_F(")
                _append_signature(kwd.definition, context, out, indent + 1, None, translation)
                out.append(f"{pad}),")
            continue

        type_str = _format_type(kwd.definition.get("typ", "?"))
        statut = kwd.definition.get("statut", "?")
        required = statut == "o"
        has_default = "defaut" in kwd.definition and kwd.definition["defaut"] is not None

        # Python convention: "required" = no default, "optional" = has default.
        # For code_aster keywords that are optional without a declared default,
        # we use Python's ellipsis literal `...` as a conventional "unspecified"
        # sentinel, which keeps the fence valid Python.
        if required:
            line = f"{pad}{key}: {type_str},"
        elif has_default:
            default = _format_value(kwd.definition["defaut"])
            line = f"{pad}{key}: {type_str} = {default},"
        else:
            line = f"{pad}{key}: {type_str} = ...,"

        out.append(line)


def _render_keyword(name: str, kwd, parent_cmd) -> str:
    parent_name = parent_cmd.name if hasattr(parent_cmd, "name") else str(parent_cmd)
    translation = _translation_of(parent_cmd) if hasattr(parent_cmd, "definition") else {}

    doc = _udocstring(kwd, key=name, translation=translation)

    out: list[str] = []
    # 1. Signature — the main readout.
    out.append("```python")
    if _is_factor(kwd):
        out.append(f"{name}=_F(")
        _append_signature(kwd.definition, context=None, out=out, indent=1, translation=translation)
        out.append(")")
    else:
        type_str = _format_type(kwd.definition.get("typ", "?"))
        statut = kwd.definition.get("statut", "?")
        required = statut == "o"
        has_default = "defaut" in kwd.definition and kwd.definition["defaut"] is not None
        if required:
            out.append(f"{name}: {type_str}")
        elif has_default:
            out.append(f"{name}: {type_str} = {_format_value(kwd.definition['defaut'])}")
        else:
            out.append(f"{name}: {type_str} = ...")
    out.append("```")

    # 2. Description.
    if doc:
        out.append("")
        out.append(f"*{_escape_italic(doc)}*")

    # 3. Details — status / allowed / range / rules collapsed into one block.
    details: list[str] = []
    status = kwd.definition.get("statut", "?")
    details.append(f"- {_t('status')}: **{_status_label(status)}**")
    into = kwd.definition.get("into")
    if into:
        literals = " | ".join(_format_value(v) for v in into)
        details.append(f"- {_t('allowed_values')}:")
        details.append("")
        details.append("  ```python")
        details.append(f"  {literals}")
        details.append("  ```")
    val_min = kwd.definition.get("val_min")
    val_max = kwd.definition.get("val_max")
    if val_min is not None or val_max is not None:
        lo = val_min if val_min is not None else "−∞"
        hi = val_max if val_max is not None else "+∞"
        details.append(f"- {_t('range')}: `[{lo}, {hi}]`")
    if details:
        out.append("")
        out.extend(details)

    rules = _rules_to_bullets(getattr(kwd, "_rules", None))
    if rules:
        out.append("")
        out.append(f"**{_t('rules')}**")
        for r in rules:
            out.append(f"- {r}")

    # 4. Footer — doc link with a separator.
    _append_doc_link(out, parent_name)
    return "\n".join(out) + "\n"


def _status_label(statut: str) -> str:
    mapping = {
        "o": _t("required"),
        "f": _t("optional"),
        "d": _t("optional_defaulted"),
        "c": _t("cached"),
    }
    return mapping.get(statut, statut)


def _clean_condition(cond: str) -> str:
    return re.sub(r"\s+", " ", (cond or "").strip())
