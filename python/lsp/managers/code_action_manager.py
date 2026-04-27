"""Quick-fix code actions for diagnostics emitted by DiagnosticsManager.

The dispatch lives entirely off `Diagnostic.code` and the `data` payload
each diagnostic carries — no recomputation of fuzzy matches.
"""

from __future__ import annotations

import sys

from lsprotocol.types import (
    CodeAction,
    CodeActionKind,
    Diagnostic,
    TextEdit,
    WorkspaceEdit,
)
from managers.diagnostics_manager import (
    CODE_UNKNOWN_COMMAND,
    CODE_UNKNOWN_KWARG,
    CODE_VALUE_NOT_IN_INTO,
)


def _log(msg: str) -> None:
    sys.stderr.write(msg + "\n")
    sys.stderr.flush()


class CodeActionManager:
    def actions(self, doc_uri: str, diagnostics: list[Diagnostic]) -> list[CodeAction]:
        out: list[CodeAction] = []
        for d in diagnostics or []:
            try:
                out.extend(self._actions_for(doc_uri, d))
            except Exception as exc:
                _log(f"[codeAction] crashed for code={d.code}: {exc!r}")
        return out

    def _actions_for(self, doc_uri: str, d: Diagnostic) -> list[CodeAction]:
        code = getattr(d, "code", None)
        data = _data_dict(d)
        if code == CODE_UNKNOWN_COMMAND:
            return self._replace_actions(
                doc_uri, d, "Replace with `{cand}`", data.get("candidates") or []
            )
        if code == CODE_UNKNOWN_KWARG:
            return self._replace_actions(
                doc_uri, d, "Rename to `{cand}`", data.get("candidates") or []
            )
        if code == CODE_VALUE_NOT_IN_INTO:
            allowed = data.get("allowed") or []
            # Emit a quick fix per allowed value, quoted as the user
            # would have typed it (strings get single quotes).
            literals = [_format_literal(v) for v in allowed]
            return self._replace_actions(doc_uri, d, "Replace with `{cand}`", literals)
        return []

    def _replace_actions(
        self,
        doc_uri: str,
        d: Diagnostic,
        title_template: str,
        candidates: list[str],
    ) -> list[CodeAction]:
        out: list[CodeAction] = []
        for cand in candidates[:6]:
            try:
                edit = WorkspaceEdit(changes={doc_uri: [TextEdit(range=d.range, new_text=cand)]})
                out.append(
                    CodeAction(
                        title=title_template.format(cand=cand),
                        kind=CodeActionKind.QuickFix,
                        diagnostics=[d],
                        edit=edit,
                        is_preferred=(cand == candidates[0]),
                    )
                )
            except Exception as exc:
                _log(f"[codeAction] could not build edit for {cand!r}: {exc!r}")
        return out


def _data_dict(d: Diagnostic) -> dict:
    raw = getattr(d, "data", None)
    if isinstance(raw, dict):
        return raw
    # pygls may surface .data as an attrs-style object; do best-effort.
    out: dict = {}
    for k in ("candidates", "allowed", "name", "keyword", "rule", "args"):
        try:
            v = getattr(raw, k)
            if v is not None:
                out[k] = v
        except Exception:
            continue
    return out


def _format_literal(v) -> str:
    if isinstance(v, str):
        # Heuristic: numeric strings are tags like "0"/"1" that should stay bare.
        try:
            float(v)
            return v
        except (TypeError, ValueError):
            return f"'{v}'"
    return str(v)
