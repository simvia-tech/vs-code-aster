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

from ..Commons import *
from ..Language.DataStructure import *
from ..Language.Syntax import *

DEFI_LIST_ENTI = OPER(
    nom="DEFI_LIST_ENTI",
    op=22,
    sd_prod=listis_sdaster,
    fr=tr("Définir une liste d'entiers strictement croissante"),
    reentrant="n",
    OPERATION=SIMP(statut="f", typ="TXM", defaut="DEFI", into=("DEFI", "NUME_ORDRE")),
    # définition d'une liste d'entiers
    # ----------------------------------
    b_defi=BLOC(
        condition="""equal_to("OPERATION", 'DEFI')""",
        regles=(UN_PARMI("VALE", "DEBUT"), EXCLUS("VALE", "INTERVALLE")),
        VALE=SIMP(statut="f", typ="I", max="**"),
        DEBUT=SIMP(statut="f", typ="I"),
        INTERVALLE=FACT(
            statut="f",
            max="**",
            regles=(UN_PARMI("NOMBRE", "PAS"),),
            JUSQU_A=SIMP(statut="o", typ="I"),
            NOMBRE=SIMP(statut="f", typ="I", val_min=1),
            PAS=SIMP(statut="f", typ="I", val_min=1),
        ),
    ),
    # extraction d'une liste de nume_ordre dans une sd_resultat :
    # ------------------------------------------------------------
    b_extr=BLOC(
        condition="""equal_to("OPERATION", 'NUME_ORDRE')""",
        RESULTAT=SIMP(statut="o", typ=resultat_sdaster),
        PARAMETRE=SIMP(statut="o", typ="TXM"),
        INTERVALLE=FACT(
            statut="o",
            max="**",
            fr=tr("Définition des intervalles de recherche"),
            VALE=SIMP(statut="o", typ="R", min=2, max=2),
        ),
    ),
    INFO=SIMP(statut="f", typ="I", defaut=1, into=(1, 2)),
    TITRE=SIMP(statut="f", typ="TXM"),
)
