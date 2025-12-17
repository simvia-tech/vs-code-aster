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

# person_in_charge: natacha.bereux at edf.fr

from ..Commons import *
from ..Language.DataStructure import *
from ..Language.Syntax import *


def elim_lagr_prod(MATR_RIGI, **args):
    if args.get("__all__"):
        return (matr_asse_elim_r,)

    if AsType(MATR_RIGI) == matr_asse_depl_r:
        return matr_asse_elim_r
    raise AsException("type de concept resultat non prevu")


ELIM_LAGR = OPER(
    nom="ELIM_LAGR",
    op=69,
    sd_prod=elim_lagr_prod,
    fr=tr("Créer une matrice en ayant éliminé les condition cinématiques dualisées."),
    reuse=SIMP(statut="c", typ=CO),
    # Matrice de "rigidité" (celle qui contient les équations dualisées) :
    MATR_RIGI=SIMP(statut="o", typ=(matr_asse_depl_r,)),
    # Matrice à réduire (si ce n'est pas la matrice de rigidité) :
    MATR_ASSE=SIMP(statut="f", typ=(matr_asse_depl_r,)),
    INFO=SIMP(statut="f", typ="I", into=(1, 2)),
)
