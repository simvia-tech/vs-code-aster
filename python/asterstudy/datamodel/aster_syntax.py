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
code_aster Syntax Interface
---------------------------

Implementation of the interface to the code_aster commands catalog.

"""


import importlib
import os.path as osp
import sys


class SyntaxId:
    """Container of the id of syntax objects.

    This list of type identifiers can be extended but never change between
    two releases of code_aster.
    """
    __slots__ = ()
    simp, fact, bloc, command = list(range(4))

IDS = SyntaxId()


def is_unit_valid(unit):
    """Tell `unit` is a valid logical unit number."""
    try:
        unit = int(str(unit))
        assert unit > 0
        assert unit not in [0, 1, 6]
    except (TypeError, ValueError, AssertionError):
        return False
    return True


def get_cata_typeid(obj):
    """Get the type identifier of the code_aster syntax object.
    Return -1 if if *obj* is not a code_aster syntax object.

    Returns:
        int: type identifier
    """
    try:
        typeid = obj.getCataTypeId()
    except (TypeError, AttributeError):
        typeid = -1
    return typeid


def _import_aster(path, package):
    """Import a package of code_aster catalog from path.
    """
    root, vers = osp.split(path)
    sys.path.insert(0, path)
    try:
        package_path = "code_aster.{0}".format(package)
        module = importlib.import_module(package_path, vers)
    except Exception as exc: # pylint: disable=broad-except
        import traceback
        msg = ("Can not import package '{3}' for version '{1}' from {0}\n"
               "Reason: {2}".format(root, vers, traceback.format_exc(),
                                    package))
        raise ImportError(msg + '\n' + str(exc)) from exc
    finally:
        sys.path.pop(0)
    return module


def import_aster(path):
    """Import the code_aster catalog from path.

    Example: ``path = /path/to/catalogue/vers``

    *path* contains the *code_aster* package.
    """
    # to force reload
    # pylint: disable=consider-iterating-dictionary
    for pkg in list(sys.modules.keys()):
        if pkg.startswith('code_aster.') or pkg == 'code_aster':
            del sys.modules[pkg]
    mods = {}
    for pkg in ("", "aster_version", "Commons", "Commands", "DataStructure",
                "Syntax", "SyntaxChecker", "SyntaxObjects", "SyntaxUtils"):
        sep = "." if pkg else ""
        mods[pkg] = _import_aster(path, "Cata" + sep + pkg)
    return mods
