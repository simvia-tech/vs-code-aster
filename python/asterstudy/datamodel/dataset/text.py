# -*- coding: utf-8 -*-

# Copyright 2016 EDF R&D
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License Version 3 as
# published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, you may download a copy of license
# from https://www.gnu.org/licenses/gpl-3.0.

"""
Text DataSet
------------

Implementation of *TextDataSet*.

"""


from ...common import debug_message, no_new_attributes, to_unicode
from ..abstract_data_model import add_parent
from ..catalogs import CATA
from ..command import Command
from .base import DataSet


class PatchedDataSet(DataSet):
    """Implementation of a semi graphical and text dataset.
    """

    __setattr__ = no_new_attributes(object.__setattr__)

    def __init__(self):
        """Create dataset."""
        DataSet.__init__(self)
        self._text = ""

    def __len__(self):
        """No definition for this *hybrid* dataset."""
        raise NotImplementedError('must be subclassed')

    def add_command(self, command_type, name=None):
        """Add a command into the dataset.

        Arguments:
            command_type (str): Type of the command (in a catalogue).
            name (Optional[str]): Name of the command. Defaults to
                *None*; in this case name is automatically generated for
                the command.

        Returns:
            Command: Command just added.
        """
        cata = CATA.get_catalog(command_type)
        checker = CATA.package('SyntaxChecker').checkCommandSyntax
        command = Command.factory(name, command_type, cata, checker)

        self._model.add(command, self)

        return command

    def update_commands(self, defs):
        """Update the commands returned by the dataset.

        Arguments:
            defs (list[(str, str, str)]): List of the definitions of the
                commands: *(name, title, type)*.
        """
        existing = [i.name for i in self.commands if i.name != "_"]

        # Delete existing commands that are not in 'defs'
        defs_keys = [i[0] for i in defs]
        for name in existing:
            cmd = self[name]
            if name not in defs_keys:
                cmd.delete()
            else:
                cmd.reset_dependencies()

        # Add new commands
        previous = None
        for name, title, typ in defs:
            if name in existing:
                cmd = self[name]
            else:
                try:
                    if title == '_CONVERT_VARIABLE':
                        expr = {'I':'1', 'R':'1.0', 'TXM':'"1"'}.get(typ)
                        cmd = self.add_variable(name, expr)
                    else:
                        cmd = self.add_command(title, name)
                        cmd.printable_type = typ

                except (AttributeError, TypeError) as exc:
                    debug_message("update_commands: skip", name, title, typ, str(exc))
                    if name not in existing:
                        cmd.delete()
                else:
                    # not to add the same object twice
                    existing.append(name)

                    # Add a fake dependency between commands to fix the order.
                    # This allows to check the stage without raising Naming error.
                    if previous:
                        add_parent(cmd, previous)
                    previous = cmd

    def delete_commands(self, dels):
        """Update the list of commands deleted by the text dataset.

        Arguments:
            dels (list[str]): List of the names of the deleted commands.
        """
        # Delete existing DETRUIRE commands
        for cmd in self.commands:
            if cmd.is_deleter:
                cmd.delete()

        previous = dict((i.name, i) for i in
                        self.stage.preceding_commands(None, only_preceding=True))
        lres = [previous.get(name) for name in dels if previous.get(name)]
        if lres:
            destroy = self.add_command("DETRUIRE", "_")
            destroy.init({"NOM": lres})

class TextDataSet(PatchedDataSet):
    """Implementation of the text dataset.

    Contains only the text of a code_aster commands file.
    """

    _mode = DataSet.textMode

    _text = None
    __setattr__ = no_new_attributes(object.__setattr__)

    def __init__(self):
        """Create dataset."""
        PatchedDataSet.__init__(self)
        self._text = ""

    @property
    def text(self):
        """str: Attribute that holds *text* of the TextDataSet."""
        return self._text

    @text.setter
    def text(self, text):
        self._text = to_unicode(text)

    def __len__(self):
        """Get the dataset length: number of lines in the text.

        Returns:
            int: Length of dataset which is equal to the number of lines
            of the text.
        """
        return len(self._text.strip().splitlines())

    def append_text(self, text):
        """Append text to the content.

        Arguments:
            text (str): Text being added.
        """
        self._text += to_unicode(text)

    def __mul__(self, other):
        """Support native Python '*' operator protocol."""
        assert self.text == other.text

    def initialize_copy(self):
        """
        Create a copy with no connections.

        Text is copied into content"""

        res = self.__class__()
        res.text = self.text
        return res

    @property
    def sorted_commands(self):
        """Returns the list of commands (as *commands*) because the commands
        are not ordered in a Text dataset.
        """
        return self.commands
