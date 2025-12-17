from command_core import CommandCore
from command_registry import CommandRegistry

class UpdateManager:
    """
    Manager for handling document open and change events for .comm files.
    """

    def __init__(self):
        self.core = CommandCore()

    def init_registry(self, doc, doc_uri):
        """
        Initialize the registry when a document is opened.
        """
        ls = self.core.get_ls()
        registry = CommandRegistry()
        registry.initialize(ls, doc.lines)
        self.core.set_registry(doc_uri, registry)

        commands = registry.get_all_commands()
        lines = [f"Document opened: {doc_uri}, {len(commands)} commands detected"]
        for key, value in commands.items():
            lines.append(f"  - {key} → {value}")
        self.core.log("\n".join(lines))

    def update_registry(self, doc, doc_uri, changes):
        """
        Incrementally update the registry on document changes.
        """
        ls = self.core.get_ls()
        registry = self.core.get_registry(doc_uri)
        if registry is None:
            registry = CommandRegistry()
            registry.initialize(ls, doc.lines)
            self.core.set_registry(doc_uri, registry)

        for change in changes:
            if hasattr(change, 'range') and change.range:
                start_line = change.range.start.line + 1
                end_line = change.range.end.line + 1
                text = change.text

                # Handle multi-line deletions or additions
                if end_line - start_line > 0 or text.count('\n') > 0 or text == '(':
                    self.core.log("on reload entierement")
                    registry.initialize(ls, doc.lines)
                    continue

                # Update the affected command (single line change)
                registry.on_document_change(doc.lines, start_line, text)

            else:
                registry.initialize(ls, doc.lines)
