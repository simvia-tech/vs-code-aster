"""
Robust architecture for code_aster command management
Updated on each keystroke, error isolation, optimistic parsing
"""

import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field


@dataclass
class CommandInfo:
    """Information about a detected command"""
    name: str  # Ex: "AFFE_CHAR_MECA"
    var_name: Optional[str]  # Ex: "CHARD" or None
    start_line: int  # 1-based numbering
    end_line: Optional[int]  # None if incomplete
    end_char: Optional[int] # Position of closing parenthesis on end line
    zone_end: int  # End of the zone (next command or EOF)
    is_complete: bool
    parsed_params: Dict[str, str] = field(default_factory=dict)
    
    def get_key(self) -> str:
        """Returns the unique key of the command"""
        return f"{self.name}:{self.start_line}"
    
    def contains_line(self, line: int) -> bool:
        """Checks if a line belongs to this command's zone"""
        return self.start_line <= line <= self.zone_end


class CommandRegistry:
    """
    Command registry with incremental updates (Unique for each .comm file)
    """
    
    def __init__(self):
        self.commands: Dict[str, CommandInfo] = {}
        # Sorted ranges for binary search: (start, end, cmd_key)
        self.ranges: List[Tuple[int, int, Optional[str]]] = []
        
    def initialize(self, ls, lines: List[str]):
        """
        Full registry initialization when opening the document
        
        Args:
            lines: All document lines
        """
        self.ls = ls
        self.commands = {}
        
        # 1. Detect all commands with the existing parser
        raw_commands = self._parse_all_commands(lines)
        
        # 2. Create CommandInfo with zones
        for cmd_data in raw_commands:
            cmd_info = CommandInfo(
                name=cmd_data['name'],
                var_name=cmd_data['var_name'],
                start_line=cmd_data['start_line'],
                end_line=cmd_data['end_line'],
                zone_end=cmd_data['zone_end'],
                end_char=cmd_data['end_char'],
                is_complete=cmd_data['is_complete']
            )
            
            # 3. Parse level 1 parameters
            cmd_info.parsed_params = self._parse_params_level1(
                lines, cmd_info.start_line, cmd_info.zone_end
            )
            
            self.commands[cmd_info.get_key()] = cmd_info
        
        # 4. Build the range index
        self._rebuild_ranges()
    
    def on_document_change(self, lines: List[str], change_start_line: int, text_change: str) -> None:
        """
        Incremental update on a change
        
        Args:
            lines: New complete document lines
            change_start_line: Line where change starts (1-based)
            text_change: Inserted text or empty
        """
        
        # 2. Find the affected command
        affected_cmd_key = self._find_command_at_line(change_start_line)
        
        if affected_cmd_key is None:
            self.ls.send_notification('logParser', {'text': f"Change outside a command"})
            return
        
        # Check if we are inside the command (needs updating end_char)
        self.ls.send_notification('logParser', {'text': f"Command: {affected_cmd_key}, change: {text_change}"})

        self._reparse_command(lines, affected_cmd_key)
        
            
    def get_command_at_line(self, line: int) -> Optional[CommandInfo]:
        """
        Returns the command that contains the given line
        
        Args:
            line: Line number (1-based)
            
        Returns:
            CommandInfo or None
        """
        cmd_key = self._find_command_at_line(line)
        return self.commands.get(cmd_key)
    
    def get_all_commands(self) -> Dict[str, str]:
        """
        Returns a simple JSON format for compatibility
        
        Returns:
            Dict {cmdName:line: "start-end" or "start"}
        """
        result = {}
        for cmd_key, cmd_info in self.commands.items():
            if cmd_info.is_complete:
                result[cmd_key] = f"{cmd_info.start_line}-{cmd_info.end_line}"
            else:
                result[cmd_key] = str(cmd_info.start_line)
        return result
    
    def log_command(self, cmd_info):
        if cmd_info.is_complete:
            lines = [f"For the complete command: {cmd_info.name}"]
            lines.append(f"start_line: {cmd_info.start_line}, end_line: {cmd_info.end_line}, zone_end: {cmd_info.zone_end}")
            lines.append(str(cmd_info.parsed_params))
            return "\n".join(lines)
        else:
            lines = [f"For the incomplete command: {cmd_info.name}"]
            lines.append(f"start_line: {cmd_info.start_line}, end_line: {cmd_info.end_line}, zone_end: {cmd_info.zone_end}")
            lines.append(str(cmd_info.parsed_params))
            return "\n".join(lines)
    
    def log_all_commands(self):
        """
        Returns all expanded commands
        """
        lines = []
        for cmd_key, cmd_info in self.commands.items():
            if cmd_info.is_complete:
                lines.append(f"For the complete command: {cmd_info.name}")
                lines.append(f"start_line: {cmd_info.start_line}, end_line: {cmd_info.end_line}, zone_end: {cmd_info.zone_end}")
                lines.append(str(cmd_info.parsed_params))
                lines.append("")
            else:
                lines.append(f"For the incomplete command: {cmd_info.name}")
                lines.append(f"start_line: {cmd_info.start_line}, end_line: {cmd_info.end_line}, zone_end: {cmd_info.zone_end}")
                lines.append(str(cmd_info.parsed_params))
                lines.append("")
        return "\n".join(lines)
    
    def text_is_outside_command(self, position, cmd_info) -> bool:
        """
        Indicates if the position is outside the command,
        only when line == cmd_info.end_line - 1 (0-based).
        
        True  => right of closing parenthesis => outside command
        False => left or inside the command => inside
        """
        # Closing parenthesis is before position.character -> we are out
        if hasattr(cmd_info, "end_char") and cmd_info.end_char is not None:
            return position.character > cmd_info.end_char
        
        return True
    
    def clean_value(self, value: str) -> str:
        value = value.strip().rstrip(',')
        if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
            value = value[1:-1]
        return value
    
    # ============ Private methods ============

    def _parse_all_commands(self, lines: List[str]) -> List[Dict]:
        """Parse all commands in the document"""
        commands = []
        pattern = re.compile(
            r'^\s*(?:(\w+)\s*=\s*)?(?!_F\b)([A-Z_][A-Z0-9_]*)\s*\(',
            re.MULTILINE
        )
        
        i = 0
        while i < len(lines):
            line = lines[i]
            
            # Skip comments
            if self._is_comment_line(line):
                i += 1
                continue
            
            match = self._find_command_start(line)
            if match:
                start_line = i + 1  # 1-based
                
                # Find command end
                result = self._find_command_end(lines, i, match['open_paren_pos'])
                
                # Calculate zone_end (adjusted later)
                zone_end = result['end_line'] if result['complete'] else len(lines)
                
                commands.append({
                    'name': match['command'],
                    'var_name': match['variable'],
                    'start_line': start_line,
                    'end_line': result['end_line'] if result['complete'] else None,
                    'end_char': result.get('end_char'),
                    'zone_end': zone_end,
                    'is_complete': result['complete']
                })
                
                if result['complete']:
                    i = result['end_line']
                else:
                    i += 1
            else:
                i += 1
        
        # Adjust zone_end
        for idx, cmd in enumerate(commands):
            if cmd['is_complete'] :
                continue
            if idx < len(commands) - 1:
                # Zone ends before next command
                cmd['zone_end'] = commands[idx + 1]['start_line'] - 1
            else:
                # Last command: zone until the end
                cmd['zone_end'] = len(lines)
        
        return commands
    
    def _parse_params_level1(self, lines: List[str], start_line: int, 
                            zone_end: int) -> Dict[str, str]:
        """
        Parse level 1 parameters (without entering _F)
        
        Args:
            lines: All lines
            start_line: Start line (1-based)
            zone_end: Zone end line (1-based)
            
        Returns:
            Dict {param_name: value}
        """
        params = {}
        
        # Extract zone content
        zone_lines = lines[start_line - 1:zone_end]
        content = '\n'.join(zone_lines)
        
        # Find first opening parenthesis
        match = re.search(r'\(', content)
        if not match:
            return params
        
        # Parse from parenthesis
        content = content[match.end():]
        
        # Regex for param=value at level 1
        # Stop at comma or closing parenthesis
        i = 0
        paren_depth = 0
        current_param = None
        value_start = None
        
        while i < len(content):
            char = content[i]
            
            # Skip strings
            if char in ('"', "'"):
                quote = char
                i += 1
                while i < len(content) and content[i] != quote:
                    if content[i] == '\\':
                        i += 2
                    else:
                        i += 1
                i += 1
                continue
            
            # Parenthesis management
            if char == '(':
                paren_depth += 1
            elif char == ')':
                paren_depth -= 1
                if paren_depth < 0:
                    # End of command - save current param before exiting
                    if current_param and value_start is not None:
                        value = content[value_start:i].strip().rstrip(',')
                        value = self.clean_value(content[value_start:i])
                        params[current_param] = value
                    break
            
            # Detect param=
            if paren_depth == 0:
                param_match = re.match(r'\s*(\w+)\s*=\s*', content[i:])
                if param_match:
                    if current_param and value_start is not None:
                        # Save previous param
                        value = content[value_start:i].strip().rstrip(',')
                        value = self.clean_value(content[value_start:i])
                        params[current_param] = value
                    
                    current_param = param_match.group(1)
                    i += param_match.end()
                    value_start = i
                    continue
                
                # Detect end of value (comma at level 0)
                if char == ',' and current_param and value_start is not None:
                    value = content[value_start:i].strip()
                    value = self.clean_value(content[value_start:i])
                    params[current_param] = value
                    current_param = None
                    value_start = None
            
            i += 1
        
        # Note: Last param is NOT saved here because either:
        # - It was saved during break (paren_depth < 0)
        # - Or the command is incomplete and we do not want partial value
        
        # Simplify _F(...) values 
        for key, value in params.items():
            if value.strip().startswith('_F('):
                params[key] = "_F(...)"
            elif value.strip().startswith('(') and '_F(' in value:
                params[key] = "(_F(...), ...)"
        
        return params

    
    def _reparse_command(self, lines: List[str], cmd_key: str):
        """Re-parse a specific command after modification"""
        cmd_info = self.commands[cmd_key]
        
        cmd_info.parsed_params = self._parse_params_level1(
            lines, cmd_info.start_line, cmd_info.zone_end
        )

        # TODO: update last character 

    
    def _find_command_at_line(self, line: int) -> Optional[str]:
        """Binary search to find the command at a line"""
        left, right = 0, len(self.ranges) - 1
        
        while left <= right:
            mid = (left + right) // 2
            start, end, cmd_key = self.ranges[mid]
            
            if start <= line <= end:
                return cmd_key
            elif line < start:
                right = mid - 1
            else:
                left = mid + 1
        
        return None
    
    def _rebuild_ranges(self):
        """Rebuild the range index for binary search"""
        self.ranges = []
        
        sorted_cmds = sorted(self.commands.values(), key=lambda c: c.start_line)
        
        current_line = 1
        for cmd_info in sorted_cmds:
            # Add empty zone before this command if needed
            if current_line < cmd_info.start_line:
                self.ranges.append((current_line, cmd_info.start_line - 1, None))
            
            # Add the command
            self.ranges.append((cmd_info.start_line, cmd_info.zone_end, cmd_info.get_key()))
            current_line = cmd_info.zone_end + 1
        
        # Add final empty zone if needed
        if self.ranges and self.ranges[-1][1] < float('inf'):
            # We cannot know the exact end, leave open
            pass
    
    # ============ Parsing utilities ============

    def _is_comment_line(self, line: str) -> bool:
        stripped = line.lstrip()
        return stripped.startswith('#') or stripped == ''
    
    def _find_command_start(self, line: str) -> Optional[Dict]:
        line_clean = self._remove_inline_comment(line)
        pattern = re.compile(
            r'^\s*(?:(\w+)\s*=\s*)?(?!_F\b)([A-Z_][A-Z0-9_]*)\s*\('
        )
        match = pattern.search(line_clean)
        if match:
            return {
                'variable': match.group(1),
                'command': match.group(2),
                'open_paren_pos': match.end() - 1
            }
        return None
    
    def _find_open_paren_pos(self, line: str) -> int:
        """Find the position of the opening parenthesis"""
        return line.find('(')
    
    def _remove_inline_comment(self, line: str) -> str:
        in_string = False
        string_char = None
        
        for i, char in enumerate(line):
            if char in ('"', "'"):
                if not in_string:
                    in_string = True
                    string_char = char
                elif char == string_char and (i == 0 or line[i-1] != '\\'):
                    in_string = False
                    string_char = None
            
            if char == '#' and not in_string:
                return line[:i]
        
        return line
    

    
    def _find_command_end(self, lines: List[str], start_idx: int, 
                         start_char_pos: int) -> Dict:
        """Find the end of a command (parser version)"""
        paren_count = 1
        i = start_idx
        char_pos = start_char_pos + 1
        
        while i < len(lines) and paren_count > 0:
            line = lines[i]
            line_clean = self._remove_inline_comment(line)
            
            # Check for new command
            if i > start_idx:
                new_cmd = self._find_command_start(line)
                if new_cmd is not None:
                    return {'end_line': i, 'complete': False}
            
            in_string = False
            string_char = None
            
            while char_pos < len(line_clean):
                char = line_clean[char_pos]
                
                if char in ('"', "'"):
                    if not in_string:
                        in_string = True
                        string_char = char
                    elif char == string_char and (char_pos == 0 or line_clean[char_pos-1] != '\\'):
                        in_string = False
                        string_char = None
                
                if not in_string:
                    if char == '(':
                        paren_count += 1
                    elif char == ')':
                        paren_count -= 1
                        if paren_count == 0:
                            return {'end_line': i + 1, 'end_char': char_pos, 'complete': True}                
                char_pos += 1
            
            i += 1
            char_pos = 0
        
        return {'end_line': len(lines), 'complete': False}
