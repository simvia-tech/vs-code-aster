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
Hidden Command
--------------

Implementation of the Hidden as a specfic Command sub class.

"""


from ...common import no_new_attributes
from .basic import Command

class Hidden(Command):
    """Special command to store a result of a macro-command.

    Macro-commands can create results that are not direct results of the
    operator (on the left of the equal sign).
    This syntax is not Python compliant but must be supported to work with
    the current versions of code_aster.

    *Hidden* allows to manage the creation of these additional results
    with a valid Python syntax.

    This looks like::

        # code_aster syntax
        res1 = MACRO_COMMAND(RESULT2=CO('res2'), <other keywords...>)
        ANOTHER(USE=res2)

        # asterstudy objects (symbolic)
        macro = Command(RESULT2=CO('res2'), ...)
        hidden = Hidden(DECL=<CO object>, PARENT=macro)

        # asterstudy objects (API)
        macro = stage('MACRO_COMMAND', 'res1')
        macro['RESULT2'] = 'res2'
        hidden = stage['res2']

    The *Hidden* is automatically created when a keyword with type 'CO'
    is assigned in the parent *Command*.

    """
    specific_name = '_RESULT_OF_MACRO'
    _parent_id = None
    __setattr__ = no_new_attributes(object.__setattr__)

    @property
    def parent_id(self):
        """Attribute that holds the uid of the parent *Command*."""
        # store id no to add cyclic reference
        return self._parent_id

    def init(self, storage, duplication=False, conversion=False, file_check=False):
        """Initializes its context from an outside dictionary"""
        self._parent_id = storage['PARENT'].uid
        super().init(storage, duplication=duplication, conversion=conversion, file_check=file_check)

    def accept(self, visitor):
        """Walks along the objects tree using the visitor pattern."""
        visitor.visit_hidden(self)

    def _register_cos(self, _, dummy):
        """Overrides corresponding 'Command._register_cos' method with dummy."""

    def initialize_copy(self):
        """Creates a copy with no connections."""
        return Hidden(self.name, self.title, self.cata, self._syntax_checker)

    def finalize_copy(self, orig, **kwargs):
        """
        Hook function: attune data model additionally after a Hidden
        has been copied.

        Updates parent id.

        Arguments:
            orig (Hidden): Original Hidden object freshly replicated.
            map_of_copies (dict): Map `node: copieded_node`.
        """
        super().finalize_copy(orig, **kwargs)

        dups = kwargs['map_of_copies']
        new_parent = dups[self._model.get_node(orig.parent_id)]
        self._parent_id = new_parent.uid
