try:
    from asterstudy.datamodel.catalogs import CATA
except ImportError as exc:
    raise Exception(f"Could not import CATA from asterstudy.datamodel.catalogs. Ensure the path is correct. {sys.path} ; {exc}")

class CommandCore:
    """
    Singleton managing global objects and utilities:
    - CATA reference
    - Document registries (CommandRegistry per doc)
    - Langage server utilities
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.CATA = CATA
            cls._instance.document_registries = {}
        return cls._instance
    
    # ====== Langage server ======

    def store_ls(self, ls):
        """Store the LanguageServer instance."""
        self.ls = ls

    def log(self, debug):
        self.ls.send_notification('logParser', {'text': debug})

    def get_ls(self):
        return self.ls
    
    def get_doc_from_uri(self, doc_uri):
        return self.ls.workspace.get_document(doc_uri)
    
    # ====== CATA ======

    def get_CATA(self):
        """Get the CATA object"""
        return self.CATA
    
    def get_CATA_commands(self):
        return self.CATA.get_commands()

    def get_docstring(self, command_name):
        return self.CATA.get_command_definition(command_name, context = None)
    
    def get_command_def(self, command_name):
        cmd_obj = self.CATA.get_command_obj(command_name)
        if cmd_obj:
            cmd_def = self.CATA.parse_command(cmd_obj)
            return cmd_def
    
    # ====== Document registries ======

    def get_registry(self, doc_uri):
        """Return the CommandRegistry for a given document URI, or None"""
        return self.document_registries.get(doc_uri)

    def set_registry(self, doc_uri, registry):
        """Associate a CommandRegistry instance to a document URI"""
        self.document_registries[doc_uri] = registry

    def remove_registry(self, doc_uri):
        """Remove a registry for a closed/removed document"""
        if doc_uri in self.document_registries:
            del self.document_registries[doc_uri]


