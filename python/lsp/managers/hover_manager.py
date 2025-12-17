"""
HoverManager: provides hover information for code_aster commands
Relies on CommandCore to get the document registry and CATA metadata
"""
import re
from command_core import CommandCore

from lsprotocol.types import (
    Hover,
    MarkupContent,
    MarkupKind,
)

class HoverManager:
    """
    Manager for providing hover info in a code_aster document.
    """

    def __init__(self):
        self.core = CommandCore()

    def display(self, doc_uri, position) -> Hover | None:
        """
        Return a Hover object for the given document URI and position.
        """
        doc = self.core.get_doc_from_uri(doc_uri)
        line_text = doc.lines[position.line]
        word = self.extract_word_at_position(line_text, position.character)

        if word:
            docstring = self.core.get_docstring(word)
            if docstring:
                return Hover(contents=MarkupContent(
                    kind=MarkupKind.PlainText,
                    value=docstring
                ))
    
    def extract_word_at_position(self, line: str, char_pos: int) -> str:
        matches = list(re.finditer(r'\b\w+\b', line))
        for match in matches:
            if match.start() <= char_pos <= match.end():
                return match.group()
        return ""
    

