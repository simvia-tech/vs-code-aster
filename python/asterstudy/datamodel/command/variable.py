# -*- coding: utf-8 -*-

# Copyright 2016 EDF R&D i
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
Variable Command
----------------

Implementation of the Variable as a specfic Command sub class.

"""


# The pragma below has to be removed after migration to Python 3 and
# suppression of above two lines.
# pragma pylint: disable=wrong-import-position,wrong-import-order

from ...common import (CyclicDependencyError, debug_message, format_expr,
                       no_new_attributes)
from ..abstract_data_model import add_parent, remove_parent
from ..catalogs import CATA
from ..general import ConversionLevel, Validity
from .basic import Command
from .constancy import ModifiesCommandInstance as ModifiesInstance


class Variable(Command):
    """Special command to store expression of user variables."""
    name_length = 999
    specific_name = '_CONVERT_VARIABLE'

    _evaluated = _updating = None
    __setattr__ = no_new_attributes(object.__setattr__)

    def __init__(self, *args, **kwargs):
        """Constructor"""
        Command.__init__(self, *args, **kwargs)
        self._evaluated = None
        self._updating = False

    def initialize_copy(self):
        """Create a copy with no connections."""
        return Variable(self.name, self.title, self.cata, self._syntax_checker)

    @staticmethod
    def initial_context():
        """Returns `initial` Python context (independent of Stage and Command)

        Returns:
            dict: pairs of name per corresponding Python instance.
        """
        import math
        context = {}
        for func in dir(math):
            if not func.startswith('_'):
                context[func] = getattr(math, func)

        return context

    @staticmethod
    def context(stage, variable=None):
        """Returns `current` Python context for the given Command.

        Returns:
            dict: pairs of name per corresponding Python instance.
        """
        dataset = stage.dataset

        # First, collect all Variables (even from preceding Stages)
        commands = []
        for preceding_stage in dataset.preceding_stages:
            if preceding_stage.is_graphical_mode():
                commands.extend(preceding_stage.dataset.commands)

        for command in dataset.commands:
            if command is variable: # skip self
                continue

            commands.append(command)

        # Finally, compose the target 'context'
        context = Variable.initial_context()
        var_type = CATA.package("DataStructure").PythonVariable
        for command in commands:
            name = command.name
            if name == '' or command.type is not var_type:
                continue

            context[name] = command.evaluation

        return context

    @property
    def current_context(self):
        """Returns `current` Python context for the given Command.

        Returns:
            dict: pairs of name per corresponding Python instance.
        """
        stage = self.stage

        return Variable.context(stage, self)

    @property
    def all_variables(self):
        """Return all existing variable."""
        def _is_variable(item):
            return isinstance(item, type(self))

        stage = self.stage
        if not stage:
            return ()
        commands = list(stage[self:])[1:] # pragma pylint: disable=invalid-slice-index
        variables = [j for j in commands if _is_variable(j)]

        if stage.parent_case: # may be None during deletion
            stages = list(stage.parent_case[stage:])[1:]
            for i in [i for i in stages if i.is_graphical_mode()]:
                variables.extend([j for j in i if _is_variable(j)])

        return variables

    def _propagate_modifications(self, others=None):
        """Recursively update all its children + *other* commands."""
        commands = set(self.child_variables).union(others or [])
        commands.discard(self)
        for child in commands:
            child.update()

    @property
    def child_variables(self):
        """Variables using this one in their expression"""
        return [var for var in self.child_commands if isinstance(var, Variable)]

    def _after_rename(self):
        """Called when variable is renamed."""
        Command._after_rename(self)
        self._propagate_modifications(self.all_variables)

    def before_remove(self):
        """Prepares to remove the variable from the model"""
        self.update(expression='', name='')

        return Command.before_remove(self)

    def _reset_dependencies(self):
        """Cleanup dependencies to other variables."""
        for parent in self.parent_nodes:
            if isinstance(parent, Variable):
                remove_parent(self, parent)

    def _update_dependencies(self, current_context):
        """Find out and assign new dependencies."""
        self._reset_dependencies()
        stage = self.stage
        dataset = stage.dataset

        # Find available command names (excluding 'initial' ones)
        initial_context = Variable.initial_context()
        names = set(current_context.keys()) - set(initial_context.keys())
        try:
            code_obj = compile(self.expression, '<string>', 'exec')
            parent_names = set(code_obj.co_names) - set([self.name])
            for name in parent_names:
                if name not in names:
                    continue # Skip 'predefined' variables (like 'pi')
                # in Python2, there was a try/except because of list comprehension
                command = dataset[name]
                if command.depends_on(self):
                    msg = "'{0.name}' -> '{1.name}'".format(command, self)
                    raise CyclicDependencyError(msg)
                add_parent(self, command)
        except SyntaxError:
            pass

    def update(self, expression=None, name=None):  # pragma pylint: disable=inconsistent-return-statements
        """Evaluates assigned expressions in the `current` context.
        The expression of the formula is updated (reordering is called via
        `init()`).

        Ensure to be not recursive.

        Returns:
            dict: pairs of name per Python instance.
        """
        if self._updating:
            return
        self._updating = True
        debug_message("updating variable", repr(self))
        try:
            return self._update(expression, name)
        finally:
            self._updating = False

    def _update(self, expression=None, name=None):
        """Evaluates assigned expressions in the `current` context.

        Returns:
            dict: pairs of name per Python instance.
        """
        if name is not None:
            self.name = name

        if expression is not None: # Use given expression
            self.expression = format_expr(expression)

        if self.expression == '': # Return if the given expression is empty
            # self.expression = ''
            self._evaluated = None
            self._check_validity = True
            # update children before resetting dependencies
            self._propagate_modifications()
            self._reset_dependencies()
            return self._evaluated

        # Evaluation of the given expression
        current_context = self.current_context
        try:
            self._check_validity = True
            self._evaluated = eval(self.expression, current_context) # pragma pylint: disable=eval-used
        except (SyntaxError, TypeError, NameError):
            self._evaluated = None

        self._update_dependencies(current_context)
        self._propagate_modifications()

        return self._evaluated

    def check(self, mode=Validity.Complete, safe=True):
        """Checks given validity aspect and return corresponding status"""
        if not self._check_validity and mode == Validity.Complete:
            return self._validity

        result = Command.check(self, mode, safe)

        # all commands are valid in a text stage: no keyword, no dependency
        if not self.stage.is_text_mode():
            if mode & Validity.Syntaxic:
                if self.evaluation is None:
                    result |= Validity.Syntaxic

        if mode == Validity.Complete:
            self._validity = result
            self._check_validity = False

        return result

    @property
    def evaluation(self):
        """misc: Evaluation of the variable in the initial context."""
        if self._evaluated is None:
            self.update()
        return self._evaluated

    @property
    def expression(self):
        """Return the exprerssion of the variable."""
        storage = self.storage_nocopy
        return storage['EXPR'] if 'EXPR' in storage else ''

    @expression.setter
    def expression(self, value):
        """misc: Set the variable expression."""
        self.init({'EXPR': format_expr(value)})

    @ModifiesInstance(True)
    def init(self, storage, duplication=None, conversion=False, file_check=False):
        """Initializes its context from an outside dictionary"""

        self._storage.clear()

        self._storage.update(storage)

        self.update()

        self.submit(file_check)

    def gettype(self, strict=ConversionLevel.Type):
        """Return the type of the value."""
        ntype = type(self.evaluation)
        # for lists and tuples, return the type of the first element
        if ntype in (list, tuple) and self._evaluated:
            ntype = type(self._evaluated[0])

        if ntype == float:
            return 'R'

        if ntype == int:
            return 'R'

        if issubclass(ntype, str):
            return 'TXM'

        return None

    def accept(self, visitor):
        """Walks along the objects tree using the visitor pattern."""
        visitor.visit_variable(self)

    def name_exists(self, name):
        """Tell if `name` is an existing Variable name.

        Arguments:
            name (str): Proposed name.

        Returns:
            bool: *True* if another Variable with this name already exists.
        """
        return name in self.current_context
