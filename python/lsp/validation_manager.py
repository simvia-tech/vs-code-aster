"""Whole-study validation for the "Validate Current Study" command.

Unlike the edit-time `DiagnosticsManager` (which validates a single open
`.comm` buffer keystroke by keystroke), this manager looks at the study as a
whole: it cross-checks the `.comm` against its `.export` and produces a
structured report consumed by the TypeScript side to render both the Problems
panel diagnostics and the validation report webview.

Two levels of checks:
  1. Command / concept validity inside the `.comm` (syntactic, dependency,
     naming, used).
  2. I/O validity between `UNITE=` values used in the `.comm` and the file
     units declared in the `.export`.

Everything is defensive: the catalog has quirks and we never want this to
raise. On failure we degrade to an empty / partial report.
"""

from __future__ import annotations

import keyword
import re
import sys
import traceback

from command_core import CommandCore
from command_registry import CommandRegistry
from export_parser import DIR_IN, DIR_OUT, IMPLICIT_TYPES, parse_export
from validators import (
    co_output_names,
    command_return_types,
    expected_classes,
    find_keyword,
    is_bare_identifier,
    simp_defaults,
)

_UNITE_RE = re.compile(r"\bUNITE\s*=\s*(\d+)")

# Commands whose `UNITE=` keyword denotes an input (read) or output (write)
# file. We key off the conventional code_aster verb prefixes and back them up
# with an explicit list for the common cases so the direction check is
# reliable on the commands the report is most likely to see.
_INPUT_COMMANDS = {
    "LIRE_MAILLAGE",
    "LIRE_RESU",
    "LIRE_TABLE",
    "LIRE_CHAMP",
    "LIRE_FONCTION",
    "PRE_GIBI",
    "PRE_GMSH",
    "PRE_IDEAS",
}
_OUTPUT_COMMANDS = {
    "IMPR_RESU",
    "IMPR_TABLE",
    "IMPR_FONCTION",
    "IMPR_GENE",
    "IMPR_CO",
    "IMPR_MACR_ELEM",
}


def _log(msg: str) -> None:
    sys.stderr.write(msg + "\n")
    sys.stderr.flush()


def _command_unit_direction(name: str) -> str | None:
    """Best-effort direction for a command's `UNITE=` file.

    Returns DIR_IN, DIR_OUT, or None when we can't tell (in which case the
    direction-mismatch check is skipped for that unit)."""
    if name in _INPUT_COMMANDS or name.startswith("LIRE_") or name.startswith("PRE_"):
        return DIR_IN
    if name in _OUTPUT_COMMANDS or name.startswith("IMPR_"):
        return DIR_OUT
    return None


class ValidationManager:
    def __init__(self):
        self.core = CommandCore()

    # --------------------------------------------------------------- entry

    def validate_study(self, comm_text: str, export_text: str | None) -> dict:
        """Validate a whole study. Always returns a report dict; never raises."""
        try:
            return self._validate_study(comm_text, export_text or "")
        except Exception as exc:
            _log(f"[validation] validate_study crashed: {exc!r}\n{traceback.format_exc()}")
            return {"commands": [], "io": [], "diagnostics": [], "hasExport": False}

    def _validate_study(self, comm_text: str, export_text: str) -> dict:
        lines = comm_text.split("\n")
        registry = CommandRegistry()
        registry.initialize(None, lines)
        cata = self.core.get_CATA()

        commands = list(registry.commands.values())

        # concept name -> (start_line_1based, command_name)
        var_index: dict[str, tuple[int, str]] = {}
        for ci in commands:
            if ci.var_name and ci.var_name not in var_index:
                var_index[ci.var_name] = (ci.start_line, ci.name)
            # `CO("name")` declares a concept even without an assignment
            # (e.g. ASSE_ELEM_SSD); register those so later references resolve.
            for name in co_output_names(lines, ci):
                if name not in var_index:
                    var_index[name] = (ci.start_line, ci.name)

        diagnostics: list[dict] = []
        rows: list[dict] = []
        for ci in commands:
            row = self._check_command(lines, ci, cata, var_index, diagnostics)
            rows.append(row)

        io_rows, io_diags = self._check_io(lines, commands, export_text)
        diagnostics.extend(io_diags)

        return {
            "commands": rows,
            "io": io_rows,
            "diagnostics": diagnostics,
            "hasExport": bool(export_text.strip()),
        }

    # ------------------------------------------------ command/concept level

    def _check_command(self, lines, ci, cata, var_index, diagnostics) -> dict:
        concept = ci.var_name or "[noname]"
        cmd_obj = None
        try:
            cmd_obj = cata.get_command_obj(ci.name)
        except Exception:
            cmd_obj = None

        syntactic = cmd_obj is not None and ci.is_complete

        # When the command isn't recognised (or is unbalanced) the other
        # checks have nothing reliable to work with: report them as N/A.
        if not syntactic:
            return {
                "concept": concept,
                "command": ci.name,
                "line": ci.start_line - 1,
                "syntactic": False,
                "dependency": None,
                "naming": None,
                "used": None,
            }

        produces = bool(command_return_types(cmd_obj))

        dependency = self._check_dependency(lines, ci, cmd_obj, var_index, diagnostics)
        naming = self._check_naming(lines, ci, produces, var_index, diagnostics)
        used = self._check_used(lines, ci, produces, diagnostics)

        return {
            "concept": concept,
            "command": ci.name,
            "line": ci.start_line - 1,
            "syntactic": True,
            "dependency": dependency,
            "naming": naming,
            "used": used,
        }

    def _check_dependency(self, lines, ci, cmd_obj, var_index, diagnostics) -> bool:
        """Top-level keyword values that reference a concept must resolve to a
        concept defined *before* this command."""
        ok = True
        try:
            context = simp_defaults(cmd_obj.definition)
        except Exception:
            context = {}
        try:
            context.update(ci.parsed_params or {})
        except Exception:
            pass

        for key, value in (ci.parsed_params or {}).items():
            if not is_bare_identifier(value):
                continue
            ref = value.strip().rstrip(",").strip()
            # Only treat it as a concept dependency when the keyword actually
            # expects a data-structure type — otherwise it's a plain literal.
            try:
                kwd = find_keyword(cmd_obj.definition, key, context)
                if kwd is None or not expected_classes(kwd):
                    continue
            except Exception:
                continue
            defined = var_index.get(ref)
            if defined is None:
                ok = False
                diagnostics.append(
                    self._diag(
                        "comm",
                        ci.start_line - 1,
                        lines,
                        ci.name,
                        "error",
                        "dependency",
                        f"Undefined concept `{ref}` used in keyword `{key}` of `{ci.name}`.",
                        locate=(key, ref),
                    )
                )
            elif defined[0] >= ci.start_line:
                ok = False
                diagnostics.append(
                    self._diag(
                        "comm",
                        ci.start_line - 1,
                        lines,
                        ci.name,
                        "error",
                        "dependency",
                        f"Concept `{ref}` is used in `{ci.name}` before it is defined.",
                        locate=(key, ref),
                    )
                )
        return ok

    def _check_naming(self, lines, ci, produces, var_index, diagnostics) -> bool:
        """Naming consistency. Produces warnings, never blocking errors."""
        ok = True
        # A command that produces a concept but is left unnamed.
        if produces and not ci.var_name:
            ok = False
            diagnostics.append(
                self._diag(
                    "comm",
                    ci.start_line - 1,
                    lines,
                    ci.name,
                    "warning",
                    "naming",
                    f"`{ci.name}` produces a concept but the result is not assigned to a name.",
                )
            )
            return ok
        if not ci.var_name:
            return ok
        name = ci.var_name
        if not name.isidentifier() or keyword.iskeyword(name):
            ok = False
            diagnostics.append(
                self._diag(
                    "comm",
                    ci.start_line - 1,
                    lines,
                    ci.name,
                    "warning",
                    "naming",
                    f"`{name}` is not a valid concept name.",
                )
            )
        # Redefinition: the same name was already assigned by an earlier command.
        # The reentrant idiom (`x = CMD(reuse=x, ...)`) deliberately reassigns
        # the same name to augment the concept in place — not a redefinition.
        reuse_val = ""
        try:
            reuse_val = (ci.parsed_params or {}).get("reuse", "") or ""
            reuse_val = reuse_val.strip().rstrip(",").strip()
        except Exception:
            reuse_val = ""
        is_reentrant = reuse_val == name
        defined = var_index.get(name)
        if defined is not None and defined[0] < ci.start_line and not is_reentrant:
            ok = False
            diagnostics.append(
                self._diag(
                    "comm",
                    ci.start_line - 1,
                    lines,
                    ci.name,
                    "warning",
                    "naming",
                    f"Concept `{name}` is redefined (first defined at line {defined[0]}).",
                )
            )
        return ok

    def _check_used(self, lines, ci, produces, diagnostics):
        """Whether a produced concept is referenced later. Returns None (N/A)
        for commands that don't produce a concept or whose result is unnamed."""
        if not produces or not ci.var_name:
            return None
        name = ci.var_name
        pattern = re.compile(rf"\b{re.escape(name)}\b")
        after = "\n".join(lines[ci.zone_end :])
        if pattern.search(after):
            return True
        diagnostics.append(
            self._diag(
                "comm",
                ci.start_line - 1,
                lines,
                ci.name,
                "warning",
                "unused",
                f"Concept `{name}` is defined by `{ci.name}` but never used.",
            )
        )
        return False

    # ----------------------------------------------------------- I/O level

    def _comm_units(self, lines, commands) -> dict[int, list[dict]]:
        """Map unit -> list of `{command, direction, line, col_start, col_end}`
        occurrences found via literal `UNITE=<int>` in each command body."""
        units: dict[int, list[dict]] = {}
        for ci in commands:
            start = ci.start_line - 1
            end = ci.zone_end
            for li in range(start, min(end, len(lines))):
                line = lines[li]
                # Ignore comments.
                code = line.split("#", 1)[0]
                for m in _UNITE_RE.finditer(code):
                    unit = int(m.group(1))
                    units.setdefault(unit, []).append(
                        {
                            "command": ci.name,
                            "direction": _command_unit_direction(ci.name),
                            "line": li,
                            "col_start": m.start(1),
                            "col_end": m.end(1),
                        }
                    )
        return units

    def _check_io(self, lines, commands, export_text):
        rows: list[dict] = []
        diagnostics: list[dict] = []
        comm_units = self._comm_units(lines, commands)
        export_files = parse_export(export_text)
        export_by_unit: dict[int, object] = {}
        for ef in export_files:
            export_by_unit.setdefault(ef.unit, ef)

        has_export = bool(export_text.strip())

        for unit in sorted(set(comm_units) | set(export_by_unit)):
            occ = comm_units.get(unit)
            ef = export_by_unit.get(unit)

            comm_dir = None
            comm_cmds: list[str] = []
            if occ:
                comm_cmds = [o["command"] for o in occ]
                for o in occ:
                    if o["direction"] is not None:
                        comm_dir = o["direction"]
                        break

            if occ and ef is None:
                # Used in .comm but missing from .export.
                if has_export:
                    o = occ[0]
                    diagnostics.append(
                        {
                            "file": "comm",
                            "line": o["line"],
                            "colStart": o["col_start"],
                            "colEnd": o["col_end"],
                            "severity": "error",
                            "code": "io-missing-export",
                            "message": (
                                f"UNITE={unit} is used in {comm_cmds[0]} but no matching file "
                                f"is declared in the export file."
                            ),
                        }
                    )
                rows.append(
                    {
                        "unit": unit,
                        "direction": _dir_label(comm_dir),
                        "file": "—",
                        "exportType": "—",
                        "usedIn": ", ".join(dict.fromkeys(comm_cmds)),
                        "status": "error" if has_export else "warning",
                    }
                )
            elif ef is not None and not occ:
                # Declared in .export but not used in .comm.
                implicit = ef.type in IMPLICIT_TYPES
                if not implicit:
                    diagnostics.append(
                        {
                            "file": "export",
                            "line": ef.line,
                            "colStart": ef.unit_col_start,
                            "colEnd": ef.unit_col_end,
                            "severity": "warning",
                            "code": "io-unused-export",
                            "message": (
                                f"Unit {unit} is declared in the export file but is not "
                                f"explicitly used in the command file."
                            ),
                        }
                    )
                rows.append(
                    {
                        "unit": unit,
                        "direction": _dir_label(ef.direction),
                        "file": ef.name,
                        "exportType": ef.type,
                        "usedIn": "implicit" if implicit else "—",
                        "status": "ok" if implicit else "warning",
                    }
                )
            else:
                # Present on both sides.
                status = "ok"
                if comm_dir is not None and ef.direction != comm_dir:
                    status = "error"
                    o = occ[0]
                    diagnostics.append(
                        {
                            "file": "comm",
                            "line": o["line"],
                            "colStart": o["col_start"],
                            "colEnd": o["col_end"],
                            "severity": "error",
                            "code": "io-direction",
                            "message": (
                                f"UNITE={unit} is used as {_dir_label(comm_dir).lower()} by "
                                f"{comm_cmds[0]} but is declared as {_dir_label(ef.direction).lower()} "
                                f"in the export file."
                            ),
                        }
                    )
                rows.append(
                    {
                        "unit": unit,
                        "direction": _dir_label(ef.direction),
                        "file": ef.name,
                        "exportType": ef.type,
                        "usedIn": ", ".join(dict.fromkeys(comm_cmds)) or "implicit",
                        "status": status,
                    }
                )
        return rows, diagnostics

    # --------------------------------------------------------------- helper

    def _diag(self, file, line0, lines, cmd_name, severity, code, message, locate=None) -> dict:
        """Build a comm-side diagnostic. When `locate=(key, ref)` is given we
        point the range at `ref` on the command's line(s); otherwise at the
        command name on its start line."""
        col_start, col_end, target_line = 0, 0, line0
        if locate is not None:
            key, ref = locate
            found = self._locate_ref(lines, line0, key, ref)
            if found is not None:
                target_line, col_start, col_end = found
        if col_end == 0:
            text = lines[line0] if 0 <= line0 < len(lines) else ""
            m = re.search(rf"\b{re.escape(cmd_name)}\b", text)
            if m:
                col_start, col_end = m.start(), m.end()
            else:
                col_end = max(1, len(text))
        return {
            "file": file,
            "line": target_line,
            "colStart": col_start,
            "colEnd": col_end,
            "severity": severity,
            "code": code,
            "message": message,
        }

    @staticmethod
    def _locate_ref(lines, start_line0, key, ref):
        """Find `KEY = ref` within a window after the command start; return
        (line0, col_start, col_end) of `ref`, or None."""
        pattern = re.compile(rf"\b{re.escape(key)}\s*=\s*({re.escape(ref)})\b")
        for li in range(start_line0, min(start_line0 + 60, len(lines))):
            m = pattern.search(lines[li])
            if m:
                return li, m.start(1), m.end(1)
        return None


def _dir_label(direction: str | None) -> str:
    if direction == DIR_IN:
        return "Input"
    if direction == DIR_OUT:
        return "Output"
    return "Unknown"
