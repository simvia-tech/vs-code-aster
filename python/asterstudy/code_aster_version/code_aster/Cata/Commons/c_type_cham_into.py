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

# person_in_charge: mathieu.courtois at edf.fr
#

from ..Language.DataStructure import *
from ..Language.Syntax import *
from .c_nom_grandeur import C_NOM_GRANDEUR


def C_TYPE_CHAM_INTO(type_cham=None):
    """Retourne la liste des valeurs possibles pour le mot-clef TYPE_CHAM"""
    type_cham = type_cham or ["ELEM", "ELNO", "ELGA", "CART", "NOEU"]

    types = []
    for phys in C_NOM_GRANDEUR():
        if phys != "VARI_R":
            for typ in type_cham:
                types.append(typ + "_" + phys)
        else:
            # il ne peut pas exister NOEU_VARI_R ni CART_VARI_R (il faut utiliser VAR2_R):
            for typ in type_cham:
                if typ not in ("CART", "NOEU"):
                    types.append(typ + "_" + phys)
    return tuple(types)
