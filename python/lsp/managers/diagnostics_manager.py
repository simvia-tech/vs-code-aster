"""Edit-time diagnostics for code_aster `.comm` files.

Walks each command in the registry, validates against CATA, and emits
LSP `Diagnostic` objects. Every per-command and per-keyword check is
wrapped to swallow exceptions so a CATA quirk can never block hover,
completion, or formatting.
"""

from __future__ import annotations

import re
import sys
import traceback

from command_core import CommandCore
from lsprotocol.types import (
    Diagnostic,
    DiagnosticSeverity,
    Position,
    Range,
)
from validators import (
    command_return_types,
    expected_classes,
    find_keyword,
    find_param,
    is_bare_identifier,
    required_keywords,
    simp_defaults,
    types_compatible,
    value_in_into,
    visible_keywords,
)


def _log(msg: str) -> None:
    sys.stderr.write(msg + "\n")
    sys.stderr.flush()


# Diagnostic codes (kept stable so CodeActionManager can dispatch on them).
CODE_UNKNOWN_COMMAND = "unknown-command"
CODE_UNKNOWN_KWARG = "unknown-kwarg"
CODE_VALUE_NOT_IN_INTO = "value-not-in-into"
CODE_REQUIRED_MISSING = "required-missing"
CODE_RULE_VIOLATION = "rule-violation"
CODE_UNDEFINED_VARIABLE = "undefined-variable"
CODE_TYPE_MISMATCH = "type-mismatch"
CODE_DEPRECATED = "deprecated"


_RULE_TEMPLATES = {
    "AtLeastOne": "At least one of {args} must be defined.",
    "ExactlyOne": "Exactly one of {args} must be defined.",
    "AtMostOne": "At most one of {args} may be defined.",
    "IfFirstAllPresent": "If `{first}` is set, all of {rest} must also be set.",
    "OnlyFirstPresent": "If `{first}` is set, none of {rest} may be set.",
    "AllTogether": "Either all or none of {args} must be defined.",
    "NotEmpty": "At least one keyword must be provided.",
}


class DiagnosticsManager:
    def __init__(self):
        self.core = CommandCore()
        try:
            from asterstudy.datamodel.dict_categories import DEPRECATED as _DEP

            self._deprecated = set(_DEP or [])
        except Exception:
            self._deprecated = set()

    # -------------------------------------------------------- entry

    def validate(self, doc_uri: str) -> list[Diagnostic]:
        """Validate the whole document. Always returns a (possibly empty)
        list — never raises."""
        try:
            return self._validate(doc_uri)
        except Exception as exc:
            _log(f"[diagnostics] validate({doc_uri}) crashed: {exc!r}\n{traceback.format_exc()}")
            return []

    def _validate(self, doc_uri: str) -> list[Diagnostic]:
        registry = self.core.get_registry(doc_uri)
        doc = self.core.get_doc_from_uri(doc_uri)
        if registry is None or doc is None:
            return []
        cata = self.core.get_CATA()
        diags: list[Diagnostic] = []

        # Build a `var_name → (start_line_1based, command_name)` index for
        # variable-reference / type-compat checks. The earliest assignment
        # wins on duplicates (we'll re-evaluate later if needed).
        var_index: dict[str, tuple[int, str]] = {}
        for ci in registry.commands.values():
            try:
                if ci.var_name and ci.var_name not in var_index:
                    var_index[ci.var_name] = (ci.start_line, ci.name)
            except Exception:
                continue
            # `CO("name")` inside a macro declares a future output bound
            # to `name`. Register those so later references resolve.
            try:
                end = ci.end_line if ci.end_line is not None else ci.zone_end
                start_idx = max(0, ci.start_line - 1)
                end_idx = min(len(doc.lines), end)
                body = "\n".join(doc.lines[start_idx:end_idx])
                for m in re.finditer(r"\bCO\s*\(\s*['\"]([A-Za-z_]\w*)['\"]", body):
                    name = m.group(1)
                    if name not in var_index:
                        var_index[name] = (ci.start_line, ci.name)
            except Exception:
                pass

        for ci in registry.commands.values():
            try:
                diags.extend(self._validate_command(doc.lines, registry, ci, cata, var_index))
            except Exception as exc:
                _log(f"[diagnostics] cmd={ci.name} crashed: {exc!r}")
        _log(f"[diagnostics] {doc_uri}: {len(diags)} issue(s)")
        return diags

    # -------------------------------------------------------- per command

    def _validate_command(
        self,
        lines: list[str],
        registry,
        ci,
        cata,
        var_index: dict[str, tuple[int, str]],
    ) -> list[Diagnostic]:
        diags: list[Diagnostic] = []

        # -- 1. unknown command ------------------------------------------
        cmd_obj = None
        try:
            cmd_obj = cata.get_command_obj(ci.name)
        except Exception:
            cmd_obj = None
        if cmd_obj is None:
            diags.append(self._diag_unknown_command(lines, ci, cata))
            return diags

        # -- 8. deprecated (information, doesn't gate other checks) ------
        if ci.name in self._deprecated:
            diags.append(self._diag_deprecated(lines, ci))

        # Position-aware kwarg parse.
        try:
            pairs = registry.parse_keyword_positions(lines, ci)
        except Exception:
            pairs = []

        try:
            context = simp_defaults(cmd_obj.definition)
        except Exception:
            context = {}
        try:
            context.update(ci.parsed_params or {})
        except Exception:
            pass

        try:
            cmd_def_params = self.core.get_command_def(ci.name).get("params", [])
        except Exception:
            cmd_def_params = []

        typed_names: set[str] = set()
        for pair in pairs:
            try:
                typed_names.add(pair.name)
                self._check_pair(pair, cmd_obj, cmd_def_params, context, var_index, ci, diags)
            except Exception as exc:
                _log(f"[diagnostics] pair {pair.name} in {ci.name} crashed: {exc!r}")

        # -- 4. required keywords missing in active scope ----------------
        try:
            for required in required_keywords(cmd_obj.definition, context):
                if required not in typed_names:
                    diags.append(self._diag_required_missing(lines, ci, required))
        except Exception:
            pass

        # -- 5. regles violations ---------------------------------------
        try:
            rules = getattr(cmd_obj, "_rules", None) or []
            for rule in rules:
                try:
                    diag = self._check_rule(lines, ci, rule, typed_names)
                    if diag:
                        diags.append(diag)
                except Exception:
                    continue
        except Exception:
            pass

        return diags

    # -------------------------------------------------------- per pair

    def _check_pair(self, pair, cmd_obj, cmd_def_params, context, var_index, ci, diags) -> None:
        # -- 2. unknown keyword -----------------------------------------
        kwd = find_keyword(cmd_obj.definition, pair.name, context)
        if kwd is None:
            visible_names = [n for n, _ in visible_keywords(cmd_obj.definition, context)]
            diags.append(self._diag_unknown_kwarg(pair, visible_names))
            return  # rest of the pair's checks don't apply

        # -- 3. value not in `into` (SIMP scalars only) -----------------
        param = find_param(cmd_def_params, pair.name)
        if param is not None:
            try:
                into = param.get("allowed")
                if into and not is_factor_value(pair.value):
                    if not value_in_into(pair.value, into):
                        diags.append(self._diag_value_not_in_into(pair, into))
                        # don't double-flag with type mismatch
                        return
            except Exception:
                pass

        # -- 6/7. variable reference checks -----------------------------
        if is_bare_identifier(pair.value):
            ref_name = pair.value.strip().rstrip(",").strip()
            if ref_name not in var_index:
                diags.append(self._diag_undefined_var(pair, ref_name))
                return
            assigned_line, src_cmd = var_index[ref_name]
            if assigned_line >= ci.start_line:
                diags.append(self._diag_undefined_var(pair, ref_name, used_before_def=True))
                return
            # type compatibility (only when we have classes on both sides)
            try:
                expected = expected_classes(param) if param else ()
                if expected:
                    src_obj = None
                    try:
                        src_obj = self.core.get_CATA().get_command_obj(src_cmd)
                    except Exception:
                        src_obj = None
                    if src_obj is not None:
                        var_types = command_return_types(src_obj)
                        if var_types and not types_compatible(var_types, expected):
                            diags.append(
                                self._diag_type_mismatch(pair, ref_name, var_types, expected)
                            )
            except Exception:
                pass

    # -------------------------------------------------------- diagnostic builders

    @staticmethod
    def _line_text(lines: list[str], idx: int) -> str:
        if 0 <= idx < len(lines):
            return lines[idx]
        return ""

    def _diag_unknown_command(self, lines, ci, cata) -> Diagnostic:
        # Locate the command name on its start line.
        idx = max(0, ci.start_line - 1)
        line = self._line_text(lines, idx)
        m = re.search(rf"\b{re.escape(ci.name)}\b", line)
        if m:
            rng = Range(Position(idx, m.start()), Position(idx, m.end()))
        else:
            rng = Range(Position(idx, 0), Position(idx, max(0, len(line))))
        candidates = []
        try:
            all_cmds = [c["name"] for c in cata.get_commands()]
            candidates = nearest(ci.name, all_cmds, n=3)
        except Exception:
            candidates = []
        msg = f"Unknown code_aster command `{ci.name}`."
        if candidates:
            msg += " Did you mean " + ", ".join(f"`{c}`" for c in candidates) + "?"
        return Diagnostic(
            range=rng,
            severity=DiagnosticSeverity.Error,
            code=CODE_UNKNOWN_COMMAND,
            source="code_aster",
            message=msg,
            data={"candidates": candidates, "name": ci.name},
        )

    def _diag_unknown_kwarg(self, pair, visible_names: list[str]) -> Diagnostic:
        candidates = nearest(pair.name, visible_names, n=3)
        msg = f"Unknown keyword `{pair.name}`."
        if candidates:
            msg += " Did you mean " + ", ".join(f"`{c}`" for c in candidates) + "?"
        return Diagnostic(
            range=Range(
                Position(pair.name_line, pair.name_col_start),
                Position(pair.name_line, pair.name_col_end),
            ),
            severity=DiagnosticSeverity.Error,
            code=CODE_UNKNOWN_KWARG,
            source="code_aster",
            message=msg,
            data={"candidates": candidates, "name": pair.name},
        )

    def _diag_value_not_in_into(self, pair, into) -> Diagnostic:
        rendered = ", ".join(f'"{v}"' if isinstance(v, str) else str(v) for v in into)
        return Diagnostic(
            range=Range(
                Position(pair.value_line, pair.value_col_start),
                Position(pair.value_line, pair.value_col_end),
            ),
            severity=DiagnosticSeverity.Error,
            code=CODE_VALUE_NOT_IN_INTO,
            source="code_aster",
            message=f"`{pair.value}` is not allowed for `{pair.name}`. Allowed: {rendered}.",
            data={"keyword": pair.name, "allowed": [str(v) for v in into]},
        )

    def _diag_required_missing(self, lines, ci, required: str) -> Diagnostic:
        idx = max(0, ci.start_line - 1)
        line = self._line_text(lines, idx)
        m = re.search(rf"\b{re.escape(ci.name)}\b", line)
        if m:
            rng = Range(Position(idx, m.start()), Position(idx, m.end()))
        else:
            rng = Range(Position(idx, 0), Position(idx, max(0, len(line))))
        return Diagnostic(
            range=rng,
            severity=DiagnosticSeverity.Error,
            code=CODE_REQUIRED_MISSING,
            source="code_aster",
            message=f"`{ci.name}` requires keyword `{required}` (not provided).",
            data={"keyword": required},
        )

    def _check_rule(self, lines, ci, rule, typed_names: set[str]) -> Diagnostic | None:
        cls = type(rule).__name__
        args = tuple(getattr(rule, "ruleArgs", ()) or ())
        if not args and cls != "NotEmpty":
            return None
        present = [a for a in args if a in typed_names]
        violated = False
        if cls == "AtLeastOne" and len(present) < 1:
            violated = True
        elif cls == "ExactlyOne" and len(present) != 1:
            violated = True
        elif cls == "AtMostOne" and len(present) > 1:
            violated = True
        elif cls == "IfFirstAllPresent":
            if args[0] in typed_names and any(a not in typed_names for a in args[1:]):
                violated = True
        elif cls == "OnlyFirstPresent":
            if args[0] in typed_names and any(a in typed_names for a in args[1:]):
                violated = True
        elif cls == "AllTogether":
            if 0 < len(present) < len(args):
                violated = True
        elif cls == "NotEmpty":
            if not typed_names:
                violated = True
        if not violated:
            return None
        template = _RULE_TEMPLATES.get(cls, f"{cls} rule violated.")
        first = f"`{args[0]}`" if args else ""
        rest = ", ".join(f"`{a}`" for a in args[1:]) if len(args) > 1 else ""
        joined = ", ".join(f"`{a}`" for a in args) if args else ""
        msg = template.format(args=joined, first=first, rest=rest)

        idx = max(0, ci.start_line - 1)
        line = self._line_text(lines, idx)
        m = re.search(rf"\b{re.escape(ci.name)}\b", line)
        rng = (
            Range(Position(idx, m.start()), Position(idx, m.end()))
            if m
            else Range(Position(idx, 0), Position(idx, max(0, len(line))))
        )
        return Diagnostic(
            range=rng,
            severity=DiagnosticSeverity.Error,
            code=CODE_RULE_VIOLATION,
            source="code_aster",
            message=msg,
            data={"rule": cls, "args": list(args)},
        )

    def _diag_undefined_var(self, pair, name: str, used_before_def: bool = False) -> Diagnostic:
        msg = (
            f"`{name}` is used before it is assigned."
            if used_before_def
            else f"`{name}` is not defined."
        )
        return Diagnostic(
            range=Range(
                Position(pair.value_line, pair.value_col_start),
                Position(pair.value_line, pair.value_col_end),
            ),
            severity=DiagnosticSeverity.Error,
            code=CODE_UNDEFINED_VARIABLE,
            source="code_aster",
            message=msg,
            data={"name": name},
        )

    def _diag_type_mismatch(self, pair, name: str, var_types, expected) -> Diagnostic:
        var_str = ", ".join(t.__name__ for t in var_types) or "?"
        exp_str = ", ".join(t.__name__ for t in expected) or "?"
        return Diagnostic(
            range=Range(
                Position(pair.value_line, pair.value_col_start),
                Position(pair.value_line, pair.value_col_end),
            ),
            severity=DiagnosticSeverity.Warning,
            code=CODE_TYPE_MISMATCH,
            source="code_aster",
            message=(f"`{name}` has type `{var_str}`, but `{pair.name}` expects `{exp_str}`."),
            data={"name": name, "varTypes": [t.__name__ for t in var_types]},
        )

    def _diag_deprecated(self, lines, ci) -> Diagnostic:
        idx = max(0, ci.start_line - 1)
        line = self._line_text(lines, idx)
        m = re.search(rf"\b{re.escape(ci.name)}\b", line)
        rng = (
            Range(Position(idx, m.start()), Position(idx, m.end()))
            if m
            else Range(Position(idx, 0), Position(idx, max(0, len(line))))
        )
        return Diagnostic(
            range=rng,
            severity=DiagnosticSeverity.Information,
            code=CODE_DEPRECATED,
            source="code_aster",
            message=f"`{ci.name}` is categorised as legacy / boilerplate.",
            data={"name": ci.name},
        )


def is_factor_value(raw: str) -> bool:
    """Heuristic: a value beginning with `_F(` is a factor block, not a
    SIMP scalar — `into` validation doesn't apply to it."""
    s = (raw or "").strip()
    return s.startswith("_F(") or s.startswith("(_F(") or s.startswith("(") and "_F(" in s


# ---- fuzzy match (simple Levenshtein, top-N) -------------------------------


def nearest(target: str, candidates, n: int = 3) -> list[str]:
    target = (target or "").upper()
    scored = []
    for c in candidates:
        if not isinstance(c, str):
            continue
        d = _levenshtein(target, c.upper())
        scored.append((d, c))
    scored.sort()
    # Only suggest if at least somewhat close; cap edit distance to half-length.
    cutoff = max(2, len(target) // 2)
    out = [c for d, c in scored if d <= cutoff][:n]
    return out


def _levenshtein(a: str, b: str) -> int:
    if a == b:
        return 0
    if not a:
        return len(b)
    if not b:
        return len(a)
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(
                min(
                    cur[j - 1] + 1,
                    prev[j] + 1,
                    prev[j - 1] + (0 if ca == cb else 1),
                )
            )
        prev = cur
    return prev[-1]
