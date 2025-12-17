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
Versioning
----------

This module provides versioning utilities for AsterStudy application.

Attributes:
    VERSION_MAJOR (int): Application major version number.
    VERSION_MINOR (int): Application minor version number.
    VERSION_PATCH (int): Application release version number.
    VERSION_STR (str): String representation of the application version.

    VERSION_DB_MAJOR (int): Database storage major version number.
    VERSION_DB_MINOR (int): Database storage minor version number.
    VERSION_DB_PATCH (int): Database storage release version number.
"""



from collections import namedtuple

from .configuration import CFG

# -----------------------------------------------------------------
# Version information:
#
# * First item is a version of the application:
#       _VERSION_INFO.version
#   It changes each time when new version of application is released.
#   This version is available via VERSION_MAJOR, VERSION_MINOR and
#   VERSION_PATCH attributes and core_version() function.
#
# * Second item is a version of data storage:
#       _VERSION_INFO.database_version
#   It changes only when data model's storage format is changed.
#   WARNING: currently there is no mechanism to support backward
#   compatibility (reading old stages), so this version is FROZEN
#   until such mechanism is implemented.
#   However, these attributes are kept for future improvement of
#   the serializer.
#   This version is available via VERSION_DB_MAJOR, VERSION_DB_MINOR
#   and VERSION_DB_PATCH attributes and database_version() function.
# -----------------------------------------------------------------
_VERSION_INFO = namedtuple('asterstudy_version_info', [
    'version', 'database_version'])(
        *[(0, 11, 0),
          (0, 10, 0),])

VERSION_MAJOR, VERSION_MINOR, VERSION_PATCH = _VERSION_INFO.version
VERSION_STR = "%d.%d" % (VERSION_MAJOR, VERSION_MINOR)
if VERSION_PATCH > 0:
    VERSION_STR += ".%d" % VERSION_PATCH

VERSION_DB_MAJOR, VERSION_DB_MINOR, VERSION_DB_PATCH = \
    _VERSION_INFO.database_version


def core_version():
    """
    Get the version of the application.

    Returns:
       str: Version of the application.
    """
    return VERSION_STR


def database_version():
    """
    Get the version of the database storage.

    Returns:
       str: Version of the database.
    """
    return ".".join(str(i) for i in _VERSION_INFO.database_version)


def version():
    """
    Get the version shown to the user.

    To get the version of the *core*, use ``VERSION_STR`` constant
    or ``core_version()`` function .

    Returns:
       str: Version info.
    """
    return CFG.version_label() if CFG.version_label() else core_version()
