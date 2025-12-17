# -*- coding: utf-8 -*-

# Copyright 2016 - 2018 EDF R&D
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
Formula Command
---------------

Implementation of the Formula as a specfic Command sub class.

"""


import re

from ...common import debug_message, no_new_attributes
from ..abstract_data_model import add_parent, remove_parent
from ..general import Validity
from .basic import Command
from .constancy import ModifiesCommandInstance as ModifiesInstance
from .variable import Variable


class Formula(Command):
    """Special command to store a formula."""
    specific_name = 'FORMULE'
    _expr_deps = _miss_deps = None

    __setattr__ = no_new_attributes(object.__setattr__)

    def __init__(self, *args, **kwargs):
        """Constructor"""
        Command.__init__(self, *args, **kwargs)
        self._expr_deps = []
        self._miss_deps = []

    @property
    def external_deps(self):
        """Attribute that holds the external dependencies of the formula.

        Note: The dependencies are refreshed at each access of the property.

        Returns:
            list[str]: List of the names of external objects.
        """
        # we could use _check_validity to use a cached list
        params = self['NOM_PARA'].value
        expr = self['VALE'].value or self['VALE_C'].value or ''
        self._expr_deps = external_objects(params, expr)
        return self._expr_deps

    @property
    def missing_deps(self):
        """Attribute that holds the missing dependencies of the formula.

        Returns:
            list[str]: List of the names of missing external objects.
        """
        return self._miss_deps

    @ModifiesInstance(True)
    def submit(self, file_check=False):
        """Submits the command changes into the Study"""
        super().submit(file_check)
        self._update_dependencies()

    def _update_dependencies(self):
        deps = self.external_deps
        # remove parents that are not used anymore
        for parent in self.parent_nodes[:]:
            if isinstance(parent, Command) and parent.name not in deps:
                remove_parent(self, parent)

        dataset = self.stage.dataset
        self._miss_deps = []
        for name in deps:
            try:
                parent = dataset[name]
            except StopIteration:
                self._miss_deps.append(name)
                continue
            add_parent(self, parent)

    def _check_dependencies(self, mode):
        """Checks dependencies."""
        result = super()._check_dependencies(mode)

        self._update_dependencies()
        if self._miss_deps:
            result |= Validity.Dependency

        return result

    def accept(self, visitor):
        """Walks along the objects tree using the visitor pattern."""
        visitor.visit_formula(self)


def is_func(formula, name):
    """Check if 'name' seems to be used as a function in the formula.

    Arguments:
        formula (str): Expression of the formula.
        name (str): Objects to be tested.

    Returns:
        bool: *True* if the objects is used as a function, *False* otherwise.
    """
    expr = re.compile(r'\b{0}\b\('.format(name))
    return expr.search(formula) is not None

def external_objects(params, formula):
    """Search for external functions/parameters needed by a formula.

    Arguments:
        params (list[str]): Known parameters of the formula.
        formula (str): Expression of the formula.

    Returns:
        list[str]: List of required objects.
    """
    from random import random
    if not formula.strip():
        return []
    expr = re.compile("name '(.*)' is not defined")
    needed = []
    is_ok = False
    if not isinstance(params, (list, tuple)):
        params = [params]
    context = {}
    context.update(Variable.initial_context())
    context.update(dict([p, random()] for p in params))
    while not is_ok:
        init = len(context)
        try:
            formula = ''.join(formula.splitlines())
            # pragma pylint: disable=eval-used
            eval(formula.strip(), {}, context)
            is_ok = True
        except NameError as exc:
            mat = expr.search(exc.args[0])
            if mat:
                name = mat.group(1)
                needed.append(name)
                if is_func(formula, name):
                    def _func(*_, **dummy):  # pragma pylint: disable=unused-argument
                        "A function that accepts any number of arguments."
                        return random()
                    context[name] = _func
                else:
                    context[name] = random()
        except Exception: # pragma pylint: disable=broad-except
            is_ok = False
            break
        if len(context) == init:
            break
    if not is_ok:
        debug_message("Can not evaluate formula: {0}".format(formula))
    return needed
