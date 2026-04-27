"""Command-family browser data source.

Exposes two LSP custom requests consumed by the sidebar's "Command
browser" group and the (now icon-only) status-bar nudge:
  * `codeaster/analyzeCommandFamilies` — what's in the current file,
    grouped by family. Reads from `CommandRegistry` (live, no disk
    I/O), so unsaved edits are reflected immediately.
  * `codeaster/getCompleteFamilies` — the full catalog, grouped by
    family. Used to populate the dim "browseable" entries in the
    sidebar.
"""

from command_core import CommandCore


class StatusBarManager:
    FAMILY_MAP = {
        "Mesh": "mesh",
        "Material": "material",
        "BC and Load": "bcAndLoads",
        "Analysis": "analysis",
        "Output": "output",
    }

    def __init__(self):
        self.cata = CommandCore().get_CATA()
        self.family_map = self.FAMILY_MAP

    # ----------------------------------------------------------- per file

    def analyze_command_families(self, uri: str) -> dict[str, list[str]]:
        """Walk the registry's tracked commands for `uri` and group them
        by family. Live — uses whatever the registry has, which the
        update_manager keeps in sync with `didChange`."""
        try:
            return self._analyze(uri)
        except Exception:
            return {v: [] for v in self.family_map.values()}

    def _analyze(self, uri: str) -> dict[str, list[str]]:
        registry = CommandCore().get_registry(uri)
        result: dict[str, list[str]] = {v: [] for v in self.family_map.values()}
        if registry is None:
            return result
        seen: set[str] = set()
        for cmd in registry.commands.values():
            try:
                name = cmd.name
                if name in seen:
                    continue
                seen.add(name)
                family_display = self.cata.get_command_category(name)
                family_key = self.family_map.get(family_display)
                if family_key:
                    result[family_key].append(name)
            except Exception:
                continue
        return result

    # ----------------------------------------------------------- catalog

    def get_complete_families(self) -> dict[str, list[str]]:
        """Return the complete list of catalog commands grouped by family.
        Used as the dictionary backing the sidebar's Command browser."""
        result: dict[str, list[str]] = {v: [] for v in self.family_map.values()}
        for display_name, key in self.family_map.items():
            try:
                items = self.cata.get_category(display_name)
                result[key] = list(items or [])
            except Exception:
                result[key] = []
        return result
