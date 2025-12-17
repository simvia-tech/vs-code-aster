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

# person_in_charge: georges-cc.devesa at edf.fr

from ..Commons import *
from ..Language.DataStructure import *
from ..Language.Syntax import *

CALC_FORC_NONL = OPER(
    nom="CALC_FORC_NONL",
    op=183,
    sd_prod=dyna_trans,
    reentrant="n",
    fr=tr("Créer un dyna_trans contenant des champs nommés 'DEPL' correspondant à 'FONL_NOEU' "),
    RESULTAT=SIMP(statut="o", typ=resultat_sdaster),
    regles=(
        EXCLUS(
            "TOUT_ORDRE",
            "NUME_ORDRE",
            "INST",
            "FREQ",
            "NUME_MODE",
            "NOEUD_CMP",
            "LIST_INST",
            "LIST_FREQ",
            "LIST_ORDRE",
            "NOM_CAS",
        ),
    ),
    TOUT_ORDRE=SIMP(statut="f", typ="TXM", into=("OUI",)),
    NUME_ORDRE=SIMP(statut="f", typ="I", validators=NoRepeat(), max="**"),
    NUME_MODE=SIMP(statut="f", typ="I", validators=NoRepeat(), max="**"),
    NOEUD_CMP=SIMP(statut="f", typ="TXM", validators=NoRepeat(), max="**"),
    NOM_CAS=SIMP(statut="f", typ="TXM"),
    INST=SIMP(statut="f", typ="R", validators=NoRepeat(), max="**"),
    FREQ=SIMP(statut="f", typ="R", validators=NoRepeat(), max="**"),
    LIST_INST=SIMP(statut="f", typ=listr8_sdaster),
    LIST_FREQ=SIMP(statut="f", typ=listr8_sdaster),
    LIST_ORDRE=SIMP(statut="f", typ=listis_sdaster),
    CRITERE=SIMP(statut="f", typ="TXM", defaut="RELATIF", into=("RELATIF", "ABSOLU")),
    b_prec_rela=BLOC(
        condition="""(equal_to("CRITERE", 'RELATIF'))""",
        PRECISION=SIMP(statut="f", typ="R", defaut=1.0e-6),
    ),
    b_prec_abso=BLOC(
        condition="""(equal_to("CRITERE", 'ABSOLU'))""", PRECISION=SIMP(statut="o", typ="R")
    ),
    MODELE=SIMP(statut="o", typ=modele_sdaster),
    CHAM_MATER=SIMP(statut="f", typ=cham_mater),
    CARA_ELEM=SIMP(statut="f", typ=cara_elem),
    COMPORTEMENT=C_COMPORTEMENT("MECA_NON_LINE"),
)
