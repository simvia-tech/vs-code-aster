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
Graphical DataSet
-----------------

Implementation of *GraphicalDataSet*.

"""


from ...common import debug_message, no_new_attributes
from ..abstract_data_model import Node, add_parent, remove_parent
from ..command import Command, Comment, Variable
from ..catalogs import CATA
from .base import DataSet

STARTER = 0x01
DELETED_NAMES = 0x02
DELETERS = 0x3


class GraphicalDataSet(DataSet):
    """Implementation of the graphical dataset.

    Contains a set of Command objects.

    Attributes:
        _ids (list<int>): List of Command ids that defines the order.
        _cache (dict): Cached informations.
    """

    _mode = DataSet.graphicalMode
    _ids = _cache = None
    __setattr__ = no_new_attributes(object.__setattr__)

    def __init__(self):
        """Create dataset."""
        DataSet.__init__(self)
        self._ids = []
        self._reset_cache()

    def __len__(self):
        """Get the dataset length which is the number of commands.

        Returns:
            int: Length of dataset which is equal to the number of
            commands stored in the dataset.
        """
        return self.nb_commands

    def add_command(self, command_type, name=None):
        """Reimplemented from *DataSet*."""
        cata = CATA.get_catalog(command_type)
        checker = CATA.package('SyntaxChecker').checkCommandSyntax
        command = Command.factory(name, command_type, cata, checker)

        if not name:
            name = self.stage.parent_case.generate_name(command)
            command.name = name

        last_command = self.get_last_command()

        self._model.add(command, self)

        if isinstance(last_command, Comment):
            if last_command.nb_children == 0:
                if not isinstance(command, Comment):
                    add_parent(command, last_command)

        self._set_position(command)

        return command

    def add_comment(self, content, concatenate=True):
        """Add a Comment instance into the dataset.

        Arguments:
            content (str): content of the (optionaly multiline) Comment.

        Returns:
            Comment: Comment just added.
        """
        engine = self.get_last_command() if concatenate else None

        if isinstance(engine, Comment):
            engine /= content
        else:
            engine = self.add_command(Comment.specific_name)
            engine.content = content

        return engine

    def get_cmd(self, uid):
        """Shortcut to get a command from the model."""
        return self._model.get_node(uid)

    def _reset_cache(self):
        """Reinitialize the informations about the commands ordering."""
        self._cache = dict()
        self._cache[DELETED_NAMES] = {}
        self._cache[DELETERS] = {}

    def get_ids(self):
        """Ensure that `_ids` contains all the child commands.

        Returns:
            list[int]: Current list of commands ids.
        """
        return self._ids

    def _set_position(self, command):
        """Insert a command at the right position."""
        self._before_insert(command)
        self._insert_id(command)
        self._after_insert(command)

    def _discard_position(self, command):
        """Remove an element from the list if it is a member."""
        try:
            self._ids.remove(command.uid)
        except ValueError:
            pass

    def reorder(self, command=None):
        """Ask reordering of one or all commands."""
        # debug_message(caller=True, limit=8)
        if command is None:
            self._reset_cache()
            for uid in self._ids[:]:
                self._set_position(self.get_cmd(uid))
        else:
            self._set_position(command)

    def on_remove_command(self, command):
        """Remove the command from the dataset."""
        self._clear_artificial_deps(command)
        self._discard_position(command)

    @property
    def sorted_commands(self):
        """Return the pre-sorted list of commands.

        The commands are sorted by dependency, then grouped by category and
        finally sorted by uid.

        Returns:
            list: Pre-sorted list of commands.
        """
        return [self.get_cmd(uid) for uid in self.get_ids()]

    def get_last_command(self):
        """Return the last created command.

        Returns:
            Command: Last created command (with the highest uid).
        """
        if self.is_empty():
            return None

        last_uid = self.children[-1]
        return self._model.get_node(last_uid)

    def before_remove(self):
        """Prepares to remove the dataset from the model.

        Removes commands that have been added.
        """
        self.clear()

        return Node.before_remove(self)

    def clear(self):
        """Remove all commands."""
        for command in reversed(self.commands):
            if not command.is_valid():
                continue
            command.delete()

    def initialize_copy(self):
        """
        Hook function: called when this dataset is copied.

        Bare copy: Create new empty dataset of the corresponding type.

        Returns:
            DataSet: New empty dataset.
        """
        return self.__class__()

    def finalize_copy(self, orig, **kwargs): # pragma pylint: disable=unused-argument
        """
        Hook function: custom treatments after the dataset has been copied.

        Sets all copies to *None*.

        Arguments:
            orig (DataSet): Original DataSet object freshly replicated.
        """
        for cmd in self.commands + orig.commands:
            cmd.ccopy = None

    @property
    def child_nodes(self):
        """list[Node]: Attribute that holds child nodes of the node."""
        ids = self._ids[:]
        ids.extend([uid for uid in self._children if uid not in ids])
        return [self._model.get_node(i) for i in ids]

    def _insert_id(self, command):
        """Insert a command at the right position.

        Important: It is assumed that the other commands are correctly sorted.
        """
        cmdid = command.uid
        to_check = []

        def depends_on_following(next_ids):
            """Tell if the Command depends on a command that follows."""
            deps = False
            for idj in next_ids:
                # if command is a child of cmd_idj:
                if self._model.has_path(idj, cmdid):
                    deps = True
                    break
            return deps

        self._discard_position(command)
        idx = 0

        ids = self._ids
        for i, uid in enumerate(ids):
            # if command is a child of cmd_i
            if self._model.has_path(uid, cmdid):
                pass
            # elif cmd_i is a child of command
            elif self._model.has_path(cmdid, uid):
                if not depends_on_following(ids[i + 1:]):
                    break
                to_check.append(self.get_cmd(uid))
            # no direct dependencies
            else:
                # if command depends on a command that follows,
                # do not use other criteria
                if depends_on_following(ids[i + 1:]):
                    idx += 1
                    continue
                cmd_i = self.get_cmd(uid)
                if command.categ < cmd_i.categ:
                    # debug_message("criteria: category", level=2)
                    break
                if command.categ == cmd_i.categ:
                    if command.uid < uid:
                        # debug_message("criteria: creation order", level=2)
                        break
            idx += 1

        ids.insert(idx, command.uid)
        debug_message("insert at", idx, ':', command.title, repr(command))
        for cmd in to_check:
            self.reorder(cmd)

    def _before_insert(self, current):
        """Checkings run before inserting a command.

        Arguments:
            current (Command): Command that is inserting.
        """
        if self._cache.get(STARTER):
            # all the commands except comments and variables
            # depend on the starter
            if not isinstance(current, (Comment, Variable)):
                add_parent(current, self._cache[STARTER])
        elif isinstance(current, Command) and current.is_prologue:
            self._cache[STARTER] = current

        # has an object with the same name been deleted?
        deleters = self._cache[DELETED_NAMES].get(current.name, [])
        found = False
        for delcmd in deleters:
            # is it 'current'?
            found = current in self._cache[DELETERS][delcmd.uid]
            if found:
                break
        # if 'current' has not been deleted, it must depend on all the deleters
        if not found:
            for delcmd in deleters:
                if not delcmd.depends_on(current):
                    add_parent(current, delcmd)

    def _clear_artificial_deps(self, command):
        """Clear "artifical" dependencies related to the deletion
        of a command."""
        uids = self._cache[STARTER].uid if self._cache.get(STARTER) else -1
        # remove relationship with DEBUT
        if command.uid == uids:
            for child in command.child_nodes:
                remove_parent(child, command)
            del self._cache[STARTER]

    def _after_insert(self, _):
        """Additional tasks executed after inserting a command.

        Arguments:
            current (Command): Command that is inserting.

        Returns:
            list<Command>: List of Command objects changed.
        """
        # Cached info:
        # - dict('result_name': [DETRUIRE Commands])
        # - dict(DETRUIRE Command: [deleted Commands])
        deleters = self._cache[DELETED_NAMES] = {}
        names = self._cache[DELETERS] = {}
        for uid in self._ids:
            command = self.get_cmd(uid)
            deleted = command.deletes()
            if deleted:
                names[command.uid] = deleted
                for rmcmd in deleted:
                    deleters.setdefault(rmcmd.name, []).append(command)
        return []
