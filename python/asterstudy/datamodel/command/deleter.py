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
Deleter Command
---------------

Implementation of the deleter (DETRUIRE) as a specfic Command sub class.

"""

from ...common import no_new_attributes
from .basic import Command
from .mixing import Sequence

# TODO:
# comm2study.py: _exec_command => dict(concepts détruits: deleter)
# text.py: PatchedDataSet.delete_commands


class Deleter(Command):
    """Special command to store a deleter."""

    specific_name = "DETRUIRE"
    __setattr__ = no_new_attributes(object.__setattr__)

    @property
    def is_deleter(self):
        """[bool]: *True* for the DETRUIRE command, *False* otherwise."""
        return True

    def deletes(self):
        """Return the list of results deleted by the command.

        Returns:
            list[Command]: List of Command
        """
        deleted = []
        if self._model.support["simplified_del"]:
            obj = self["NOM"].value
            # print("DEBUG: deletes, obj:", self["NOM"])
            if obj:
                deleted = obj if isinstance(obj, (list, tuple)) else [obj]
            # cleanup else NOM will be set to None and
            # 'just_created' is always False in 'Command.init()'
            if self["NOM"].undefined():
                del self._engine["NOM"]
        else: # pragma: no cover
            # used in versions < 15.4
            lfact = self["CONCEPT"]
            is_seq = isinstance(lfact, Sequence)
            if not is_seq:
                lfact = [lfact]
            for fact in lfact:
                obj = fact["NOM"].value
                obj = obj if isinstance(obj, (list, tuple)) else [obj]
                deleted.extend(obj)
            # cleanup else CONCEPT is set
            if is_seq and lfact.undefined():  # pragma pylint: disable=no-member
                del self._engine["CONCEPT"]  # pragma pylint: disable=protected-access
        # print("DEBUG: deletes:", deleted)
        return deleted
