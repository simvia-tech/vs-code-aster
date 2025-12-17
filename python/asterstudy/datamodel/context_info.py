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
Contextual informations
-----------------------

Implementation of the management of the contextual informations.

"""


class ContextualInformation:
    """Class that returns contextual informations for a Command.

    May be extended for keywords when needed.

    Args:
        obj (Command): Object for which create the contextual informations.
    """

    def __init__(self, obj):
        self._obj = obj

    def getinfo(self):  # pragma pylint: disable=no-self-use
        """Return a formated text with the informations"""
        return ""


def getinfo(obj):
    """Return the informations for the user."""
    context = ContextualInformation(obj)
    return context.getinfo()
