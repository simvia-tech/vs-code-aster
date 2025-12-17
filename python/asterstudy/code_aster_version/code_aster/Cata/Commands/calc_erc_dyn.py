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

from ..Commons import *
from ..Language.DataStructure import *
from ..Language.Syntax import *

CALC_ERC_DYN = OPER(
    nom="CALC_ERC_DYN",
    op=66,
    sd_prod=mode_meca,
    fr="Calcul de l'erreur en relation de comportement en dynamique sous une formulation fr?quentielle",
    reentrant="n",
    regles=(UN_PARMI("FREQ", "LIST_FREQ"),),
    MATR_MASS=SIMP(statut="o", typ=(matr_asse_depl_r)),
    MATR_RIGI=SIMP(statut="o", typ=(matr_asse_depl_r)),
    MATR_NORME=SIMP(statut="o", typ=matr_asse_gene_r),
    MATR_PROJECTION=SIMP(statut="o", typ=corresp_2_mailla),
    MESURE=SIMP(statut="o", typ=(dyna_harmo, mode_meca)),
    CHAMP_MESURE=SIMP(statut="f", typ="TXM", into=("DEPL", "VITE", "ACCE"), defaut="DEPL"),
    #
    FREQ=SIMP(statut="f", typ="R", validators=NoRepeat(), max="**"),
    LIST_FREQ=SIMP(statut="f", typ=listr8_sdaster),
    #
    GAMMA=SIMP(statut="o", typ="R", validators=NoRepeat()),
    ALPHA=SIMP(statut="o", typ="R", validators=NoRepeat()),
    #
    EVAL_FONC=SIMP(statut="f", typ="TXM", into=("OUI", "NON"), defaut="NON"),
    SOLVEUR=C_SOLVEUR("CALC_ERC_DYN"),
    INFO=SIMP(statut="f", typ="I", defaut=1),
    TITRE=SIMP(statut="f", typ="TXM"),
)
