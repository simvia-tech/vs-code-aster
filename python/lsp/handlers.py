# python/lsp/full_parsing.py

import asyncio
import sys

from lsprotocol.types import (
    CodeActionKind,
    CodeActionParams,
    CompletionList,
    CompletionParams,
    DidChangeTextDocumentParams,
    DidChangeWatchedFilesParams,
    DidOpenTextDocumentParams,
    Hover,
    HoverParams,
    InitializeParams,
    SignatureHelp,
    SignatureHelpParams,
)
from pygls.server import LanguageServer

from lsp.managers_container import ManagerContainer

managers = ManagerContainer()

# Per-document debounce tasks for diagnostics so we don't re-validate on
# every keystroke. Keyed by document URI.
_diag_tasks: dict[str, asyncio.Task] = {}
_DEBOUNCE_S = 0.2


def _publish_diagnostics(ls: LanguageServer, doc_uri: str) -> None:
    """Run validation and ship diagnostics to the client. Wrapped so
    that a crash in the diagnostics layer can't propagate."""
    try:
        diags = managers.diagnostics.validate(doc_uri)
        ls.publish_diagnostics(doc_uri, diags)
    except Exception as exc:
        sys.stderr.write(f"[diagnostics] publish failed: {exc!r}\n")
        sys.stderr.flush()
        try:
            ls.publish_diagnostics(doc_uri, [])
        except Exception:
            pass


def _schedule_diagnostics(ls: LanguageServer, doc_uri: str) -> None:
    """Debounce: cancel any in-flight task for this URI and queue a new
    one to fire after `_DEBOUNCE_S` seconds."""
    prev = _diag_tasks.pop(doc_uri, None)
    if prev is not None and not prev.done():
        prev.cancel()

    async def _delayed():
        try:
            await asyncio.sleep(_DEBOUNCE_S)
            _publish_diagnostics(ls, doc_uri)
        except asyncio.CancelledError:
            return

    try:
        _diag_tasks[doc_uri] = asyncio.ensure_future(_delayed())
    except RuntimeError:
        # No running loop (e.g. unit-test path) — fall back to synchronous.
        _publish_diagnostics(ls, doc_uri)


def register_handlers(server: LanguageServer):

    @server.feature("initialize")
    def on_initialize(ls: LanguageServer, params: InitializeParams):
        return {
            "capabilities": {
                "textDocumentSync": 1,
                "completionProvider": {
                    "resolveProvider": False,
                    "triggerCharacters": ["(", ",", "="],
                },
                "hoverProvider": True,
                "definitionProvider": True,
                "codeActionProvider": {
                    "codeActionKinds": [CodeActionKind.QuickFix],
                },
            }
        }

    @server.feature("textDocument/didOpen")
    def on_document_open(ls: LanguageServer, params: DidOpenTextDocumentParams):
        """Initialisation du registre à l'ouverture du document"""
        doc_uri = params.text_document.uri
        doc = ls.workspace.get_document(doc_uri)

        managers.update.init_registry(doc, doc_uri)
        _publish_diagnostics(ls, doc_uri)

    @server.feature("textDocument/didChange")
    def on_text_change(ls: LanguageServer, params: DidChangeTextDocumentParams):
        """Mise à jour incrémentale à chaque frappe"""
        doc_uri = params.text_document.uri
        doc = ls.workspace.get_document(doc_uri)

        managers.update.update_registry(doc, doc_uri, params.content_changes)
        _schedule_diagnostics(ls, doc_uri)

    @server.feature("textDocument/completion")
    def completion(ls: LanguageServer, params: CompletionParams) -> CompletionList:
        """Auto-complétion basée sur le contexte de la commande"""
        doc_uri = params.text_document.uri
        position = params.position

        return managers.completion.completion(doc_uri, position)

    @server.feature("textDocument/signatureHelp")
    def signature_help(ls: LanguageServer, params: SignatureHelpParams) -> SignatureHelp:
        doc_uri = params.text_document.uri
        position = params.position

        return managers.signature.help(doc_uri, position)

    @server.feature("textDocument/hover")
    def hover(ls: LanguageServer, params: HoverParams) -> Hover:
        doc_uri = params.text_document.uri
        position = params.position

        return managers.hover.display(doc_uri, position)

    @server.feature("textDocument/codeAction")
    def code_action(ls: LanguageServer, params: CodeActionParams):
        """Quick fixes for diagnostics. The diagnostics carry the
        candidate replacements in their `data` field, so this handler
        is just a dispatcher."""
        try:
            diags = list(getattr(params.context, "diagnostics", []) or [])
            return managers.code_action.actions(params.text_document.uri, diags)
        except Exception as exc:
            sys.stderr.write(f"[codeAction] handler crashed: {exc!r}\n")
            sys.stderr.flush()
            return []

    @server.feature("workspace/didChangeWatchedFiles")
    def ignore_watched_files(ls: LanguageServer, params: DidChangeWatchedFilesParams):
        """Handler vide pour ignorer les notifications de fichiers surveillés."""
        pass

    @server.feature("codeaster/analyzeCommandFamilies")
    def analyze_command_families(ls, params):
        if hasattr(params, "get"):
            doc_uri = params.get("uri", "unknown")
        else:
            doc_uri = getattr(params, "uri", "unknown")

        return managers.status_bar.analyze_command_families(doc_uri)

    @server.feature("codeaster/getCompleteFamilies")
    def getCompleteFamilies(ls, params):

        return managers.status_bar.get_complete_families()
