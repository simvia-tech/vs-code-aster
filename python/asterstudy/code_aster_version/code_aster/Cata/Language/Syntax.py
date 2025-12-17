# coding=utf-8
# --------------------------------------------------------------------
# Copyright (C) 1991 - 2022 - EDF R&D - www.code-aster.org
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
Objects used in catalogs
------------------------

These objects are the bricks of the code_aster language of commands.
The objects used in the description of commands are *exported*/*wrapped*
to ensure backward compatibility with the previous versions.

For example, the catalogs are using ``BLOC`` and ``FACT`` instead of
``Bloc`` and ``FactorKeyword`` that are the *Syntax Objects* internally used.
"""

import builtins

from . import DataStructure as DS
from .DataStructure import AsType
from .Rules import (
    AllTogether,
    AtLeastOne,
    AtMostOne,
    ExactlyOne,
    IfFirstAllPresent,
    NotEmpty,
    OnlyFirstPresent,
)
from .SyntaxChecker import SyntaxCheckerVisitor
from .SyntaxObjects import (
    _F,
    Bloc,
    CataError,
    FactorKeyword,
    Formule,
    ListFact,
    Macro,
    Operator,
    Procedure,
    SimpleKeyword,
)
from .Validators import (
    Absent,
    AndVal,
    Compulsory,
    LongStr,
    NoRepeat,
    AtMostOneStartsWith,
    NotEqualTo,
    OrdList,
    OrVal,
    Together,
)

builtins._F = _F


def OPER(**kwargs):
    return Operator(kwargs)


def SIMP(**kwargs):
    return SimpleKeyword(kwargs)


def FACT(**kwargs):
    return FactorKeyword(kwargs)


def BLOC(**kwargs):
    return Bloc(kwargs)


def MACRO(**kwargs):
    return Macro(kwargs)


def PROC(**kwargs):
    return Procedure(kwargs)


FIN_PROC = PROC


def FORM(**kwargs):
    return Formule(kwargs)


def OPS(kwargs):
    return kwargs


class EMPTY_OPS:
    pass


assd = DS.ASSD


class PROC_ETAPE(Procedure):
    pass


# exception
AsException = CataError

# rules
AU_MOINS_UN = AtLeastOne
UN_PARMI = ExactlyOne
EXCLUS = AtMostOne
PRESENT_PRESENT = IfFirstAllPresent
PRESENT_ABSENT = OnlyFirstPresent
ENSEMBLE = AllTogether
NON_VIDE = NotEmpty


class Translation:
    """Class to dynamically assign a translation function.

    The package Cata must stay independent. So the translation function will
    be defined by code_aster or by AsterStudy.
    """

    def __init__(self):
        self._func = lambda arg: arg

    def set_translator(self, translator):
        """Define the translator function.

        Args:
            translator (function): Function returning the translated string.
        """
        self._func = translator

    def __call__(self, arg):
        """Return the translated string"""
        if type(arg) is str:
            uarg = arg
        else:
            uarg = arg.decode("utf-8", "replace")
        return self._func(uarg)

    def __getstate__(self):
        """Does not support pickling."""
        return

    def __setstate__(self, dummy):
        """Does not support pickling."""


tr = Translation()
