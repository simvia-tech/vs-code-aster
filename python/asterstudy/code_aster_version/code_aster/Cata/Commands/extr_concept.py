# coding=utf-8
# --------------------------------------------------------------------
# Copyright (C) 1991 - 2023 - EDF R&D - www.code-aster.org
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

from ..Language.DataStructure import *
from ..Language.Syntax import *


def extr_concept_prod(self, DICT, **args):
    """Define the type of the result of EXTR_CONCEPT."""
    into = {evol_ther_dict: evol_ther}
    if args.get("__all__"):
        return tuple(into.values())

    typ = into.get(AsType(DICT))
    if not typ:
        raise AsException("Type de concept non supporté: %s %s" % (DICT, AsType(DICT)))
    return typ


EXTR_CONCEPT = MACRO(
    nom="EXTR_CONCEPT",
    op=OPS("code_aster.MacroCommands.extr_concept_ops.extr_concept_ops"),
    sd_prod=extr_concept_prod,
    DICT=SIMP(statut="o", typ=ds_dict),
    NOM=SIMP(statut="o", typ="TXM"),
)
