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
Comment
-------

Implementation of the Comment as a specfic Command sub class.

"""


from ..abstract_data_model import remove_parent
from .basic import Command

class Comment(Command):
    """Special command to store a comment."""
    specific_name = '_CONVERT_COMMENT'

    def accept(self, visitor):
        """Walks along the objects tree using the visitor pattern."""
        visitor.visit_comment(self)

    def __itruediv__(self, value):
        "To support Python native /= operator protocol"
        if not self.content.endswith('\n') and not value.startswith('\n'):
            self.content += '\n'

        self.content += value

    def __iadd__(self, value):
        "To support Python native += operator protocol"
        self.content += value

    @property
    def content(self):
        """Return comment content."""
        storage = self.storage_nocopy
        return storage['EXPR'] if 'EXPR' in storage else ''

    @content.setter
    def content(self, value):
        """misc: Set the comment content."""
        self.init({'EXPR': value})

    def before_remove(self):
        """Prepares to remove the comment from the model.

        Unregister bound commands in case.
        """
        # reset keywords value, remove command reference in all its children
        for command in self.child_nodes:
            remove_parent(command, self)

        return Command.before_remove(self)

    def unsafe_type(self):
        """A Comment does not return anything."""
        return None
