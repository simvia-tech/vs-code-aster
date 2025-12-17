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
Visitors
--------

This modules defines classes to visit content of *Command* objects (but can be
used on *DataSet* or *Stage*) and apply generic tasks, such as check values or
extract some keywords values.

"""



from .aster_syntax import IDS, get_cata_typeid
from .catalogs import CATA
from ..common import is_subclass, MeshGroupType


class AbstractVisitor:
    """Abstract visitor of a DataSet or Command."""

    def __init__(self, *args, **kwargs):
        pass

    @classmethod
    def _does_nothing(cls, dummy):
        pass

    def _visit_keysmixing_based(self, item):
        """Visit an object based on a KeysMixing."""
        keys = sorted(item.keys())
        for key in keys:
            obj = item[key]
            if obj.undefined():
                continue
            obj.accept(self)

    def visit_command(self, command):
        """Visit a command"""
        self._visit_keysmixing_based(command)

    def visit_hidden(self, dummy):
        """Visit a Hidden command"""
        self._does_nothing(dummy)

    def visit_formula(self, formula):
        """Visit a formula"""
        self.visit_command(formula)

    def visit_variable(self, var):
        """Visit a Variable"""
        self.visit_command(var)

    def visit_comment(self, dummy):
        """Visit a Comment"""
        self._does_nothing(dummy)

    def visit_factor(self, factor):
        """Visit a Factor keyword"""
        self._visit_keysmixing_based(factor)

    def visit_sequence(self, sequence):
        """Visit a Sequence of keywords."""
        for item in sequence:
            self._visit_keysmixing_based(item)

    def visit_simple(self, simple):
        """Visit a Simple keyword."""
        raise NotImplementedError


class FilterVisitor(AbstractVisitor):
    """Visitor of Command that filter the value of simple keywords.

    The keywords for which the values are matching the *checker* function are
    available using the *keywords* property as a list.

    Args:
        checker (function): Function that takes a SimpleKeyword as unique
            argument and returns a boolean.
    """

    def __init__(self, checker):
        super().__init__()
        self._checker = checker
        self._keywords = []

    @property
    def keywords(self):
        """Returns the list of filtered keywords."""
        return self._keywords

    def visit_simple(self, simple):
        """Visit a Simple keyword."""
        if self._checker(simple):
            self._keywords.append(simple)

LEVEL_2_COMMANDS = ["CALC_MODES", "MODE_STATIQUE", "MODE_NON_LINE", "DYNA_VIBRA", "PROJ_BASE",
                    "ASSE_MATRICE", "ASSE_VECTEUR"]

class GroupFilterVisitor(FilterVisitor):
    """Visitor that returns a {path: groupname} dict
          of all used groups in a Command.
    """
    PATHSEP = "."
    def __init__(self, checker):
        """
        Additional attributes:

        _basepath (list): base path of visited object relative to command.
        _group_dict (dict): {str: str} dict of returned paths ans groups.
        """
        super().__init__(checker)
        self._basepath = []
        self._group_dict = {}

    @staticmethod
    def _is_group_no(simple):
        # TODO: merge with utilities in parameterpanel.basic.CataInfo
        try:
            typ = simple.gettype()
            return _is_grno(typ)
        except: # pragma pylint: disable=bare-except
            return False

    @staticmethod
    def _is_group_ma(simple):
        # TODO: merge with utilities in parameterpanel.basic.CataInfo
        try:
            typ = simple.gettype()
            return _is_grma(typ)
        except: # pragma pylint: disable=bare-except
            return False

    @staticmethod
    def _is_group(simple):
        return GroupFilterVisitor._is_group_no(simple) \
            or GroupFilterVisitor._is_group_ma(simple)

    @staticmethod
    def _fstorage(simple, basepath):
        """Find the storage of the containing *Factor* of simple"""
        fstorage = simple._engine.storage_nocopy # pragma pylint: disable=protected-access
        if len(basepath) > 2:
            for val in basepath[2:]:
                fstorage = fstorage[int(val) if val.isdigit() else val]
        return fstorage

    def visit_command(self, command):
        """Reinitialize common path."""
        self._basepath = ['', command.cata.name]
        super().visit_command(command)

    def inc_basepath(self, key):
        """Append key to current basepath"""
        self._basepath.append(key)

    def dec_basepath(self):
        """Decrement base path"""
        self._basepath.pop(-1)

    def visit_simple(self, simple):
        """Visit a Simple keyword"""
        if self._is_group(simple):
            grtype = MeshGroupType.GElement if self._is_group_ma(simple) \
                    else MeshGroupType.GNode
            super().visit_simple(simple)
            thepath = self.PATHSEP.join(self._basepath) + \
                      self.PATHSEP + simple.name
            thegroups = simple.value
            fstorage = GroupFilterVisitor._fstorage(simple, self._basepath[:])
            if isinstance(thegroups, (list, tuple)):
                self._group_dict[thepath] = (grtype,
                                             list(thegroups),
                                             get_related(self._basepath[:],
                                                         fstorage))
            else:
                self._group_dict[thepath] = (grtype,
                                             [thegroups],
                                             get_related(self._basepath[:],
                                                         fstorage))

    @property
    def group_dict(self):
        """Found {path: groupname} values"""
        return self._group_dict

    def visit_factor(self, factor):
        """Visit a Factor keyword"""
        self.inc_basepath(factor.name)
        super().visit_factor(factor)
        self.dec_basepath()

    def visit_sequence(self, sequence):
        """Visit a Sequence of keywords."""
        self.inc_basepath(sequence.name)
        for i, item in enumerate(sequence):
            self.inc_basepath(str(i))
            self._visit_keysmixing_based(item)
            self.dec_basepath()
        self.dec_basepath()

class GroupNameFilterVisitor(GroupFilterVisitor):
    """Filter that gives all path using a given group."""

    def __init__(self, checker, groupname):
        """
        Additional attributes:

        _basepath (list): base path of visited object relative to command.
        _group_dict (dict): {str: str} dict of returned paths and groups.
        """
        super().__init__(checker)
        self._path_list = []
        self._groupname = groupname

    def visit_simple(self, simple):
        if self._is_group(simple):
            thepath = self.PATHSEP.join(self._basepath) + \
                      self.PATHSEP + simple.name
            thegroups = simple.value
            if isinstance(thegroups, (list, tuple)):
                if self._groupname in thegroups:
                    self._path_list.append(thepath)
            elif self._groupname == thegroups:
                self._path_list.append(thepath)

    @property
    def path_list(self):
        """Found paths appealing to target group"""
        return self._path_list


class UnitVisitor(FilterVisitor):
    """Visitor of Command that return the UNITE keywords.

    It is a specialization of *FilterVisitor* with a pre-treatment to skip
    commands or factor keyworsd that have no such keywords.
    """

    def __init__(self):
        def _predicate_syntax(name, simple):
            if not name.startswith("UNITE"):
                return False
            try:
                typ = simple.definition.get('typ')
                return issubclass(typ, CATA.unitds)
            except: # pragma pylint: disable=bare-except
                return False
        self._checker_type = _predicate_syntax

        def _predicate(simple):
            try:
                typ = simple.gettype()
                return issubclass(typ, CATA.unitds)
            except: # pragma pylint: disable=bare-except
                return False

        super().__init__(_predicate)

    def _visit_keysmixing_based(self, item):
        """Visit an object based on a KeysMixing."""
        # interrupt as soon as possible for performance reasons
        found = _check_cata(item.cata, self._checker_type)
        if not found:
            return

        super()._visit_keysmixing_based(item)


def _check_cata(cata, checker):
    """Recursively check a catalog definition (*Command* or *FactorKeyword*)"""
    found = False
    for name, kwd in cata.definition.iterItemsByType():
        if get_cata_typeid(kwd) == IDS.simp:
            if checker(name, kwd):
                found = True
        else:
            found = _check_cata(kwd, checker)
        if found:
            break
    return found


def obj_start(obj):
    """Helper function to represent an object."""
    txt = ""
    if isinstance(obj, list):
        txt += "["
    if isinstance(obj, tuple):
        txt += "("
    return txt


def obj_end(obj):
    """Helper function to represent an object."""
    txt = ""
    if isinstance(obj, list):
        txt += "]"
    if isinstance(obj, tuple):
        if len(obj) == 1:
            txt += ", "
        txt += ")"
    return txt

def _type_from_path(curpath):
    """
    Helper function to get the expected type of a simple from its path

    Arguments:
        curpath (list): path to keyword in the command
    """
    synobj = CATA.get_catalog(curpath[1])
    for val in curpath[2:]:
        if not val.isdigit():
            synobj = synobj.keywords.get(val)
    return synobj and synobj.definition.get('typ')

def get_related(curpath, fstorage):
    """
    Helper function to get related keywords to a simple

    Arguments:
        curpath (list): path of *Factor* instance with a group
        fstorage (dict): storage dictionary of this *Factor* instance

    Note:
        In case we're at top-level of the command, this function
            may be called with the full command dictionary.
    """
    # Process this storage

    # --- copy it, but not deepcopy the objects it may contain
    related = fstorage.copy()

    # --- drop Factors, outputs, groups, tout
    for key, val in fstorage.items():

        # Single Factor
        if isinstance(val, dict):
            related.pop(key)
            continue

        # Several occurence of Factor
        if isinstance(val, (list, tuple)) and val:
            if isinstance(val[0], dict):
                related.pop(key)
                continue

        # Drop macro outputs
        # Checking val of hidden type should suffice (see KeysMixing.__setitem__)
        #     but for safety we check the type in the catalog.
        if CATA.is_co(_type_from_path(curpath + [key])):
            related.pop(key)
            continue

        # Drop groups and tout
        if filter_groups(curpath + [key]) or filter_tout(key):
            related.pop(key)
            continue

    return related

def filter_groups(curpath): # pragma pylint: disable=unused-argument
    """Evaluates if the path leads to a group simple"""
    try:
        return expects_grma(curpath) or expects_grno(curpath)
    except (KeyError, AttributeError):
        # TODO: case encountered with CALC_MODES/NMAX_FREQ
        # Instruct if this could not lead to false negatives
        return False

def expects_grma(curpath):
    """Evaluates if the path leads to a GROUP_MA_XXX simple"""
    return _is_grma(_type_from_path(curpath))

def expects_grno(curpath):
    """Evaluates if the path leads to a GROUP_NO_XXX simple"""
    return _is_grno(_type_from_path(curpath))

def _is_grma(astype):
    """Evaluated wether astype is the group_ma type"""
    return is_subclass(astype, CATA.package('DataStructure').grma)

def _is_grno(astype):
    """Evaluated wether astype is the group_no type"""
    return is_subclass(astype, CATA.package('DataStructure').grno)

def filter_tout(key):
    """Filter out TOUT keyword"""
    return key == "TOUT"
