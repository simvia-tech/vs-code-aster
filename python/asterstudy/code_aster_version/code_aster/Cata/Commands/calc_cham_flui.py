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

# person_in_charge: hassan.berro at edf.fr

from ..Commons import *
from ..Language.DataStructure import *
from ..Language.Syntax import *

CALC_CHAM_FLUI = OPER(
    nom="CALC_CHAM_FLUI",
    op=116,
    sd_prod=evol_ther,
    fr="Calculer le champ de vitesses et de pression fluides",
    # Mot-clés obligatoires
    RIGI_THER=SIMP(statut="o", typ=matr_asse_temp_r),
    EXCIT=FACT(
        statut="o",
        max="**",
        CHARGE=SIMP(statut="o", typ=(char_ther,)),
        FONC_MULT=SIMP(statut="f", typ=(fonction_sdaster, nappe_sdaster, formule)),
    ),
    POTENTIEL=SIMP(statut="f", typ="TXM", defaut="DEPL", into=("DEPL", "VITE", "PRES")),
    DIST_REFE=SIMP(statut="f", typ="R", defaut=1.0e-2),
    MODE_MECA=SIMP(statut="o", typ=mode_meca),
    b_coefmult=BLOC(
        condition="""exists("MODE_MECA")""",
        COEF_MULT=SIMP(statut="f", typ="R", defaut=(1.0), max="**"),
    ),
)
