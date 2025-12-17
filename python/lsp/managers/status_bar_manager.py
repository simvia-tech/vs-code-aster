# status_bar.py
from pathlib import Path
import re
from typing import Dict, List
from command_core import CommandCore

class StatusBarManager:
    """
    Class that encapsulates the logic for:
      - analyzing a .comm file and returning commands by family
      - returning the complete list of known commands for each family
    """

    FAMILY_MAP = {
        'Mesh': 'mesh',
        'Material': 'material',
        'BC and Load': 'bcAndLoads',
        'Analysis': 'analysis',
        'Output': 'output'
    }

    def __init__(self):
        """
        Initialize the StatusBarManager with a CATA instance.

        Args:
            cata: The CATA catalog object from asterstudy.datamodel.catalogs
        """
        self.cata = CommandCore().get_CATA()
        self.family_map = self.FAMILY_MAP

    def analyze_command_families(self, uri: str) -> Dict[str, List[str]]:
        """
        Parse a .comm file and return the commands found in each family.

        Args:
            uri (str): URI of the .comm file,

        Returns:
            Dict[str, List[str]]: Commands grouped by family
        """
        if uri.startswith("file://"):
            path = Path(uri[7:])
        else:
            path = Path(uri)

        if not path.exists():
            return {}

        with open(path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        content = "\n".join(lines)
        return self._parse_comm_file(content)

    def get_complete_families(self) -> Dict[str, List[str]]:
        """
        Return the complete list of known commands for each family.

        Returns:
            Dict[str, List[str]]: Complete commands grouped by family
        """
        families_result = {v: [] for v in self.family_map.values()}

        for display_name, key in self.family_map.items():
            try:
                category_commands = self.cata.get_category(display_name)
                if category_commands is None:
                    category_commands = []
                families_result[key] = category_commands
            except Exception:
                families_result[key] = []

        return families_result

    def _parse_comm_file(self, content: str) -> Dict[str, List[str]]:
        """
        Parse the content of a .comm file and extract commands by family.

        Args:
            content (str): Content of the .comm file

        Returns:
            Dict[str, List[str]]: Commands grouped by family
        """
        lines = content.split('\n')
        code_without_comments = [re.sub(r'#.*$', '', l).strip() for l in lines if l.strip()]
        full_text = ' '.join(code_without_comments)

        command_pattern = r'(?:^|\s)(?:[\w]+\s*=\s*)?(?!_F\b)([A-Z][A-Z0-9_]*)\s*\('
        matches = re.finditer(command_pattern, full_text, re.VERBOSE)
        found_commands = set()
        for m in matches:
            cmd_name = m.group(1)
            if cmd_name not in ['DEBUT', 'FIN', 'POURSUITE']:
                found_commands.add(cmd_name)

        if re.search(r'\bDEBUT\s*\(', full_text):
            found_commands.add('DEBUT')
        if re.search(r'\bFIN\s*\(', full_text):
            found_commands.add('FIN')

        families_result = {v: [] for v in self.family_map.values()}
        for cmd_name in found_commands:
            try:
                family_raw = self.cata.get_command_category(cmd_name)
                family = self.family_map.get(family_raw)
                if family:
                    families_result[family].append(cmd_name)
            except Exception:
                continue

        return families_result
