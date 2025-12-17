# python/lsp/full_parsing.py

from lsprotocol.types import (
    InitializeParams,
    CompletionParams,
    CompletionList,
    HoverParams,
    Hover,
    DidChangeTextDocumentParams,
    DidOpenTextDocumentParams,
    SignatureHelp,
    SignatureHelpParams,
    DidChangeWatchedFilesParams
)

from pygls.server import LanguageServer

from lsp.managers_container import ManagerContainer
managers = ManagerContainer()

def register_handlers(server: LanguageServer):

    @server.feature("initialize")
    def on_initialize(ls: LanguageServer, params: InitializeParams) :
        return {
            "capabilities": {
                "textDocumentSync": 1,  
                "completionProvider": {
                    "resolveProvider": False,
                    "triggerCharacters": [" ", "."]
                },
                "hoverProvider": True,
                "definitionProvider": True
            }
        }
    
    @server.feature("textDocument/didOpen")
    def on_document_open(ls: LanguageServer, params: DidOpenTextDocumentParams):
        """Initialisation du registre à l'ouverture du document"""
        doc_uri = params.text_document.uri
        doc = ls.workspace.get_document(doc_uri)

        managers.update.init_registry(doc, doc_uri)

    @server.feature("textDocument/didChange")
    def on_text_change(ls: LanguageServer, params: DidChangeTextDocumentParams):
        """Mise à jour incrémentale à chaque frappe"""
        doc_uri = params.text_document.uri
        doc = ls.workspace.get_document(doc_uri)

        managers.update.update_registry(doc, doc_uri, params.content_changes)

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
    
    @server.feature("workspace/didChangeWatchedFiles")
    def ignore_watched_files(ls: LanguageServer, params: DidChangeWatchedFilesParams):
        """Handler vide pour ignorer les notifications de fichiers surveillés."""
        pass

    @server.feature("codeaster/analyzeCommandFamilies")
    def analyze_command_families(ls, params):
        if hasattr(params, 'get'):
            doc_uri = params.get('uri', 'unknown')
        else:
            doc_uri = getattr(params, 'uri', 'unknown')

        return managers.status_bar.analyze_command_families(doc_uri)
    
    @server.feature("codeaster/getCompleteFamilies")
    def getCompleteFamilies(ls, params):
        
        return managers.status_bar.get_complete_families()