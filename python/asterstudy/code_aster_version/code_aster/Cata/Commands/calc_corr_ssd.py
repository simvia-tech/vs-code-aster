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

# person_in_charge: mathieu.corus at edf.fr

from ..Commons import *
from ..Language.DataStructure import *
from ..Language.Syntax import *

CALC_CORR_SSD = OPER(
    nom="CALC_CORR_SSD",
    op=91,
    sd_prod=table_container,
    fr=tr("Qualite d'un modele reduit en dynamique"),
    reentrant="n",
    MODELE_GENE=SIMP(statut="o", typ=modele_gene),
    RESU_GENE=SIMP(statut="o", typ=mode_gene),
    UNITE=SIMP(statut="f", typ=UnitType(), defaut=8, inout="in"),
    SHIFT=SIMP(statut="f", typ="R", defaut=1.0),
    VERIF=FACT(
        statut="f",
        max="**",
        STOP_ERREUR=SIMP(statut="f", typ="TXM", defaut="OUI", into=("OUI", "NON")),
        PRECISION=SIMP(statut="f", typ="R", defaut=1.0e-3),
        CRITERE=SIMP(statut="f", typ="TXM", defaut="RELATIF", into=("RELATIF", "ABSOLU")),
    ),
    SOLVEUR=C_SOLVEUR("CALC_CORR_SSD"),
    TITRE=SIMP(statut="f", typ="TXM"),
)
