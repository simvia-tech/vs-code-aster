import sys

from command_core import CommandCore
from command_registry import CommandRegistry


def _log(msg: str) -> None:
    sys.stderr.write(msg + "\n")
    sys.stderr.flush()


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
        _log(f"[registry] init {doc_uri}: {len(commands)} commands; ranges={registry.ranges}")
        for key, value in commands.items():
            _log(f"[registry]   - {key} → {value}")

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
            if hasattr(change, "range") and change.range:
                start_line = change.range.start.line + 1
                end_line = change.range.end.line + 1
                text = change.text

                # Handle multi-line deletions or additions
                if end_line - start_line > 0 or text.count("\n") > 0 or text == "(":
                    registry.initialize(ls, doc.lines)
                    _log(
                        f"[registry] full reparse on multi-line change: "
                        f"{len(registry.get_all_commands())} commands"
                    )
                    continue

                # Update the affected command (single line change)
                registry.on_document_change(doc.lines, start_line, text)

            else:
                registry.initialize(ls, doc.lines)
                _log(
                    f"[registry] full reparse (no range): "
                    f"{len(registry.get_all_commands())} commands"
                )
