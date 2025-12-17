from lsprotocol.types import (
    CompletionList,
    CompletionItem,
    CompletionItemKind,
)
from command_core import CommandCore


class CompletionManager:
    """
    Manager responsible for providing auto-completion in code_aster .comm files.
    Fetches registries and command definitions through CommandCore.
    """

    def __init__(self):
        self.core = CommandCore()

    def completion(self, doc_uri: str, position) -> CompletionList:
        """
        Entry point called by the handler.
        Returns a CompletionList based on the command context.
        """
        registry = self.core.get_registry(doc_uri)
        if registry is None:
            return CompletionList(is_incomplete=False, items=[])
        self.core.log("completion appelée")
        cmd_info = registry.get_command_at_line(position.line + 1)
        if not cmd_info:
            return self._suggest_commands()

        return self._suggest_parameters(cmd_info)

    def _suggest_commands(self) -> CompletionList:
        """
        Suggest all available code_aster commands.
        """
        items = []
        commands = self.core.get_CATA_commands()

        for cmd in commands:  
            items.append(
                CompletionItem(
                    label=cmd["name"],
                    kind=CompletionItemKind.Function,
                    documentation=cmd.get("doc", "")
                )
            )

        return CompletionList(is_incomplete=False, items=items)


    def _suggest_parameters(self, cmd_info) -> CompletionList:
        """
        Suggest parameters of a code_aster command depending on the context.
        """
        cmd_def = self.core.get_command_def(cmd_info.name)

        if not cmd_def or "params" not in cmd_def:
            return CompletionList(is_incomplete=False, items=[])

        context = cmd_info.parsed_params.copy()

        visible_params = self._expand_condition_bloc(cmd_def["params"], context)

        items = []
        written = set(cmd_info.parsed_params.keys())
        for param in visible_params:

            if param["name"] in written:
                continue

            # Conditional bloc : we display the children parameters if it's enabled
            if param["bloc"]:
                if param["bloc"].isEnabled(context):
                    for arg in param["children"]:
                        items.append(
                            CompletionItem(
                                label=arg["name"],
                                kind=CompletionItemKind.Property,
                                insert_text=arg["name"] + "="
                            )
                        )
            # Normal parameter (can be a single param or a dico (_F))
            else:
                insert_text = param["name"] + "="
                if param["children"]:
                    insert_text += "_F"
                items.append(
                    CompletionItem(
                        label=param["name"],
                        kind=CompletionItemKind.Property,
                        insert_text=insert_text
                    )
                )

        return CompletionList(is_incomplete=False, items=items)


    def _expand_condition_bloc(self, params, context):
        """
        Expand conditional blocks depending on the current context.
        Returns a flat list of visible parameters.
        """
        visible_params = []
        for arg in params:
            if arg["bloc"]:
                if arg["bloc"].isEnabled(context):
                    for param in arg["children"]:
                        visible_params.append(param)
            else :
                visible_params.append(arg)
        return visible_params
