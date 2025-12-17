# coding=utf-8
# --------------------------------------------------------------------
# Copyright (C) 1991 - 2019 - EDF R&D - www.code-aster.org
# This file is part of code_aster.
#
# code_aster is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# code_aster is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with code_aster.  If not, see <http://www.gnu.org/licenses/>.
# --------------------------------------------------------------------

"""

This module provides versioning utilities for code_aster.

Attributes:
    VERSION_MAJOR (int): Application major version number.
    VERSION_MINOR (int): Application minor version number.
    VERSION_PATCH (int): Application release version number.
    VERSION_STR (str): String representation of the application version.
    BRANCH (str): Name of the origin branch.
"""

from collections import namedtuple

version_info = namedtuple('aster_version_info', [
'version', 'parentid', 'branch', 'date', 'from_branch', 'changes', 'uncommitted'
])(
*[(16, 7, 0),
 '5f2fdcddabc5e8a06753cfa5ebc128d93e35a4f9',
 'HEAD',
 '10/12/2024',
 'v16',
 0,
 []]
)

VERSION_MAJOR, VERSION_MINOR, VERSION_PATCH = version_info.version

VERSION_STR = "%d.%d" % (VERSION_MAJOR, VERSION_MINOR)
if VERSION_PATCH > 0:
    VERSION_STR += ".%d" % VERSION_PATCH

BRANCH = version_info.branch


def version():
    """
    Get version of application.

    Returns:
       str: Version of the application.
    """
    return VERSION_STR
