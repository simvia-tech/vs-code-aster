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

# person_in_charge: mickael.abbas at edf.fr

from ..Commons import *
from ..Language.DataStructure import *
from ..Language.Syntax import *

THER_NON_LINE_MO = OPER(
    nom="THER_NON_LINE_MO",
    op=171,
    sd_prod=evol_ther,
    fr=tr(
        "Résoudre un problème thermique non linéaire (conditions limites ou comportement matériau)"
        " stationnaire avec chargement mobile"
    ),
    reentrant="n",
    MODELE=SIMP(statut="o", typ=modele_sdaster),
    CHAM_MATER=SIMP(statut="o", typ=cham_mater),
    EXCIT=FACT(
        statut="o",
        max="**",
        CHARGE=SIMP(statut="o", typ=char_ther),
        FONC_MULT=SIMP(statut="c", typ=(fonction_sdaster, nappe_sdaster, formule)),
    ),
    ETAT_INIT=FACT(
        statut="f",
        EVOL_THER=SIMP(statut="f", typ=evol_ther),
        NUME_ORDRE=SIMP(statut="f", typ="I", defaut=0),
    ),
    CONVERGENCE=FACT(
        statut="d",
        CRIT_TEMP_RELA=SIMP(statut="f", typ="R", defaut=1.0e-3),
        CRIT_ENTH_RELA=SIMP(statut="f", typ="R", defaut=1.0e-2),
        ITER_GLOB_MAXI=SIMP(statut="f", typ="I", defaut=10),
        ARRET=SIMP(statut="c", typ="TXM", defaut="OUI", into=("OUI", "NON")),
    ),
    # -------------------------------------------------------------------
    #        Catalogue commun SOLVEUR
    SOLVEUR=C_SOLVEUR("THER_NON_LINE_MO"),
    # -------------------------------------------------------------------
    TITRE=SIMP(statut="f", typ="TXM"),
    INFO=SIMP(statut="f", typ="I", into=(1, 2)),
)
