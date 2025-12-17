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
Base services
-------------

Implementation of base classes and enumerators.

"""



from ..common import no_new_attributes, translate
from .catalogs import CATA


class UIDMixing:
    """Sub class for UID based classes.

    Arguments:
        uid (int): Object's id.
    """

    _id = None
    __setattr__ = no_new_attributes(object.__setattr__)

    def __init__(self, uid):
        self._id = uid

    @property
    def uid(self):
        """Attribute that holds unique *id*"""
        return self._id

    def __hash__(self):
        return hash((self.__class__, self.uid))

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.uid == other.uid


class CataMixing:
    """Sub class for classes based on a catalog.

    Attributes:
        _cata (PartOfSyntax): The catalog on which the object is based.
    """
    _suffix = ''
    _cata = _imposedtype = None
    __setattr__ = no_new_attributes(object.__setattr__)

    def __init__(self, cata):
        self._imposedtype = None
        self._cata = cata

    @property
    def cata(self):
        """Attribute that holds unique *cata*"""
        return self._cata

    @cata.setter
    def cata(self, value):
        "Declares setter for so named property"
        self._cata = value

    @staticmethod
    def printable_types(cata):
        """Return printable version of 'types' method."""
        names = (prod.__name__ for prod in CATA.possible_types(cata) if prod)
        return [name.replace(CataMixing._suffix, '') for name in names]

    @property
    def type(self):
        """Returns code_aster type for the given command"""
        # does not return the type! it returns the first possible type...
        if self._imposedtype:
            return self._imposedtype

        return next(iter(CATA.possible_types(self._cata)))

    @type.setter
    def type(self, value):
        """Assign code_aster type to the given command"""
        types = CATA.possible_types(self._cata)
        if (value in types or
                issubclass(value, tuple(i for i in types if i))):
            self._imposedtype = value
        else:
            raise TypeError(self.name, self.title, value) # pylint: disable=no-member

    @property
    def printable_type(self):
        """Returns printable code_aster type for the given command"""
        prod = self.type
        if prod:
            return prod.__name__
        return ''

    @printable_type.setter
    def printable_type(self, value):
        """Assign printable code_aster type to the given command"""
        package = CATA.package('DataStructure')
        self.type = getattr(package, value)

    @staticmethod
    def possible_types(command_type):
        """Return printable version of 'types' method."""
        cata = CATA.get_catalog(command_type)
        return CataMixing.printable_types(cata)


class Validity:
    """
    Enumerator for validity statuses.

    Attributes:
        Nothing: Empty (valid object).
        Syntaxic: Object is syntaxically invalid.
        Dependency: Object is invalid in terms of dependencies.
        Naming: Object is invalid in terms of naming.
        Complete: Object is invalid in all aspects.
        Valid: Same as `Nothing`.
        Any: Same as `Complete`.
    """
    Nothing = 0x00
    Ok = Valid = Nothing
    Syntaxic = 0x01
    Dependency = 0x02
    Naming = 0x04
    Complete = Syntaxic | Dependency | Naming
    Any = Complete

    @staticmethod
    def value2str(value, names=None):
        "Maps enumerator to string representation."
        result = []

        if value & Validity.Syntaxic:
            result.append(translate("AsterStudy", "Syntax problem"))
        if value & Validity.Dependency:
            result.append(translate("AsterStudy", "Broken dependencies"))
        if value & Validity.Naming:
            msg = translate("AsterStudy", "Naming conflict")
            if names:
                msg += " ({})".format(", ".join(names))
            result.append(msg)

        return "; ".join(result)


class FileAttr:
    """
    Enumerator for *UnitType* status.

    Attributes:
        No: Unknown status.
        In: Used only as input.
        Out: Used only as output.
        InOut: Used as both input and output.
        Named: Used for file used with their name during execution.
    """
    No = 0x00
    In = 0x01
    Out = 0x02
    InOut = In | Out
    Named = 0x04

    @staticmethod
    def str2value(value):
        "Maps string representation to enumerator."
        result = FileAttr.No

        if value == 'in':
            result = FileAttr.In
        elif value == 'out':
            result = FileAttr.Out
        elif value == 'inout':
            result = FileAttr.InOut

        return result

    @staticmethod
    def value2str(value):
        "Maps enumerator to string representation."
        result = ''
        if value == FileAttr.No:
            result = '?'
        if value & FileAttr.In:
            result += 'in'
        if value & FileAttr.Out:
            result += 'out'
        if value & FileAttr.Named:
            result += '+named'
        return result


# Must stay identical to `code_aster.Cata.SyntaxObjects.ConversionLevel`
class ConversionLevel:
    """
    Enumerator for the level of conversion requirements.

    Attributes:
        NoFail: Do not fail, not *strict*.
        Naming: Requires that all command results are explicitly named.
        Type: Requires a valid type definition.
        Keyword: Requires that all keywords are valid.
        Syntaxic: Requires a valid syntax of all the commands.
        Restore: Requires a conversion without error during restore.
        Any: All conversion must pass.
        Partial: Allows to make a partial conversion (to be used with
            another level).
        NoGraphical: Force to load all stages in text mode.
    """
    NoFail = 0x00
    Naming = 0x01
    Type = 0x02
    Keyword = 0x04
    Syntaxic = Naming | Type | Keyword
    Restore = 0x08
    Any = Syntaxic | Restore
    Partial = 0x10
    NoGraphical = 0x20


class CopyContext:
    """
    Defines the context in an object is copied.

    Attributes:
        Nothing: not specified
        AutoCopy: auto-copy process, e.g. when the user edits
            a stage referenced by several cases.
        UserCopy: explicit user's copy and paste operation.
    """
    Nothing = 0x00
    AutoCopy = 0x01
    UserCopy = 0x02
