# -*- coding: utf-8 -*-

# Copyright 2017 EDF R&D
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
Session
-------

The module gives informations about the current session.

The catalog can know if it is imported from AsterStudy or from a code_aster
execution and so it may behave differently.
"""



class AsterStudySession:
    """Informations about the AsterStudy session."""

    _cata = 0

    @classmethod
    def set_cata(cls):
        """Set the marker for the code_aster catalog."""
        cls._cata = 1

    @classmethod
    def use_cata(cls):
        """Tell if the code_aster catalog is used within asterstudy."""
        # code_aster legacy does not call set_cata, so it imports legacy modules
        return cls._cata == 1
