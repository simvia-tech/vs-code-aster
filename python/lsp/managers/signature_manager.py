import re
from lsprotocol.types import (
    SignatureHelp, SignatureInformation
)
from command_core import CommandCore

class SignatureManager:
    """
    Manager for providing signature help in a code_aster document.
    """

    def __init__(self):
        self.core = CommandCore() 

    def help(self, doc_uri, position):
        """
        Returns a SignatureHelp object for the given document URI and cursor position.
        """
        doc = self.core.get_doc_from_uri(doc_uri)
        if position.line >= len(doc.lines) or position.line < 0:
            self.core.log(f"[signature_help] Position line {position.line} out of range (doc has {len(doc.lines)} lines)")
            return SignatureHelp(signatures=[], active_signature=0, active_parameter=0)
        
        line_text = doc.lines[position.line][:position.character]
        
        default_signature = SignatureHelp(signatures=[], active_signature=0, active_parameter=0)

        # Match a command before the opening parenthesis
        match = re.search(r"(\w+)\s*\($", line_text)
        if match:
            cmd_name = match.group(1)
            cmd_def = self.core.get_command_def(cmd_name)
            if cmd_def:
                signature = SignatureInformation(label=self.params_label(cmd_def["params"], {}))
                return SignatureHelp(signatures=[signature], active_signature=0, active_parameter=0)

        stripped_line = line_text.rstrip()
        if stripped_line.endswith(","):
            registry = self.core.get_registry(doc_uri)
            if not registry:
                return default_signature

            cmd_info = registry.get_command_at_line(position.line + 1)
            if not cmd_info:
                return default_signature

            if cmd_info.end_line == position.line + 1:
                if registry.text_is_outside_command(position, cmd_info):
                    return default_signature

            cmd_name = cmd_info.name
            cmd_def = self.core.get_command_def(cmd_name)
            if cmd_def:
                signature = SignatureInformation(label=self.params_label(cmd_def["params"], cmd_info.parsed_params))
                self.core.log(f"Comma inside command: {cmd_name}")
                return SignatureHelp(signatures=[signature], active_signature=0, active_parameter=0)
        return default_signature


    def params_label(self, command_params, current_context):
        """
        Recursively generate a string label for the parameters of a command,
        taking into account the parameters already written by the user.
        """
        label = []
        written = set(current_context.keys())
        for param in command_params:
            if param["name"] in written:
                continue
            if param["children"]:
                if param["bloc"]:
                    if param["bloc"].isEnabled(current_context):
                        label.append(f"{self.params_label(param['children'], current_context)}")
                else:
                    label.append(f"{param['name']}: ({self.params_label(param['children'], current_context)})")
            else:
                label.append(f"{param['name']}: {param['type']}")
        return ", ".join(label)
