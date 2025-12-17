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
Base of DataSet
---------------

Implementation of base object of dataset definition.

"""


from abc import ABCMeta, abstractmethod

# The pragma below has to be removed after migration to Python 3 and
# suppression of above two lines.
# pragma pylint: disable=wrong-import-position,wrong-import-order

import itertools

from ...common import no_new_attributes
from ..command import Command, Variable
from ..abstract_data_model import Node


class DataSet(Node, metaclass=ABCMeta):
    """Implementation of the base class for datasets."""

    _mode = None
    graphicalMode = 0
    textMode = 1

    __setattr__ = no_new_attributes(object.__setattr__)

    @staticmethod
    def factory(mode):
        """Create a dataset object of the provided type.

        Arguments:
            mode (int): Type of the dataset; one of
                *DataSet.graphicalMode*, *DataSet.textMode*.

        Returns:
            DataSet: New dataset.
        """
        if mode == DataSet.graphicalMode:
            from .graphical import GraphicalDataSet
            cls = GraphicalDataSet
        elif mode == DataSet.textMode:
            from .text import TextDataSet
            cls = TextDataSet
        else:
            raise NotImplementedError("unknown mode: {0!r}".format(mode))
        return cls()

    def __init__(self):
        """Create dataset."""
        super().__init__("DataSet")
        self.deep_copy = Command

    # public interface
    @property
    def stage(self):
        """Stage: Attribute that holds a parent *Stage* of dataset."""
        return self.parent_nodes[0] if self.has_parents() else None

    @property
    def mode(self):
        """int: Attribute that holds a type of dataset.

        Result is one of *DataSet.graphicalMode*, *DataSet.textMode*.
        """
        return self._mode

    def is_graphical_mode(self):
        """Tell if the dataset is a graphical one.

        Returns:
            bool: *True* if this is a graphical dataset; *False*
            otherwise.
        """
        return self.mode == DataSet.graphicalMode

    def is_text_mode(self):
        """Tell if the dataset is a text one.

        Returns:
            bool: *True* if this is a text dataset; *False* otherwise.
        """
        return self.mode == DataSet.textMode

    def accept(self, visitor):
        """Walk along the objects tree using the visitor pattern.

        Arguments:
            visitor (any): Visitor object.
        """
        visitor.visit_dataset(self)

    @property
    def preceding_stages(self):
        """list[Stage]: Attribute that provides access to the preceding
        stages for this dataset."""
        parent_case = self.stage.parent_case
        assert parent_case
        return parent_case[:self.stage]

    @property
    def commands(self):
        """
        list[Command]: Attribute that holds list of *commands*
        associated with the dataset (sorted by dependency).
        """
        return self.subnodes(lambda node: isinstance(node, Command))

    @property
    def nb_commands(self):
        """The number of commands stored in the dataset.

        Returns:
            int: Length of dataset which is equal to the number of
            commands stored in the dataset.
        """
        return len(self.commands)

    def __len__(self):
        """Get the dataset length which is the number of commands for a
        graphical dataset and the number of text lines for a text dataset.

        Returns:
            int: Length of dataset which is equal to the number of
            commands stored or the text lines in the dataset.
        """
        raise NotImplementedError('must be subclassed')

    def is_empty(self):
        """Returns `True` if dataset has no content."""
        return len(self) == 0

    def __iter__(self):
        """Iterate over the commands stored in the dataset."""
        return iter(self.commands)

    def __contains__(self, given):
        """
        Support native Python "in" operator protocol.

        Arguments:
            given (Command or str): Command being checked.

        Returns:
            bool: *True* if Command is contained in the Stage; *False*
            otherwise.
        """
        if isinstance(given, Command):
            return next((True for command in self if command is given), False)

        return next((True for command in self if command.name == given), False)

    def __getitem__(self, given):
        """
        Support native Python ``[]`` operator protocol.

        Get particular command(s) from the Stage or DataSet:

        - ``stage[N]`` returns the ``N-1``-th command of the stage.

        - ``stage[name]`` returns the last command of the stage and its
          preceding stages that matches this ``name``.

        - ``stage[name:N]`` returns the ``N-1``-th command of the stage and its
          preceding stages that matches this ``name``.

        - ``stage[name:command]`` returns the last command of the stage and its
          preceding stages that matches this ``name`` and **does not** depend
          on ``command``.

        Note:
            *First*, *last*, or *N-1-th command* means that commands
            are sorted by dependency.

        Arguments:
            given (str, int, slice): Command's name, index or indices
                range.

        Returns:
            Command or list[Command]: Command or commands specifying
            search criterion.
        """
        # self[i] case
        if isinstance(given, int):
            return self.commands[given]

        # self[command:] case
        if isinstance(given, slice) and isinstance(given.start, Command):
            return itertools.dropwhile(lambda x: x is not given.start, self)

        commands = []
        stages = self.preceding_stages
        for stage in stages:
            commands.extend(stage.dataset.commands)

        commands.extend(self.commands)

        rcommands = reversed(commands)
        # self['name'] case
        if not isinstance(given, slice):
            return next(cmd for cmd in rcommands if cmd.name == given)

        # self[:i] case
        if isinstance(given.stop, int):
            excommands = [cmd for cmd in rcommands if cmd.name == given.start]
            return excommands[given.stop]

        # self['name':command] case
        def _predicate(item):
            return item.depends_on(given.stop)

        excommands = list(itertools.dropwhile(_predicate, rcommands))

        return next(cmd for cmd in excommands if cmd.name == given.start)

    @abstractmethod
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

    def add_variable(self, var_name, var_expr):
        """Add a Variable instance into the dataset.

        Arguments:
            var_name (str): Name of the variable.
            var_expr (str): Right side variable expression.

        Returns:
            Variable: Variable just added.
        """
        if var_name in Variable.context(self.stage):
            raise NameError("name {0!r} is already in use".format(var_name))

        engine = self.add_command(Variable.specific_name)

        engine.update(var_expr, var_name)

        return engine
