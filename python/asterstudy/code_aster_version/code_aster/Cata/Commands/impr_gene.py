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

# person_in_charge: harinaivo.andriambololona at edf.fr

from ..Commons import *
from ..Language.DataStructure import *
from ..Language.Syntax import *

IMPR_GENE = PROC(
    nom="IMPR_GENE",
    op=157,
    fr=tr(
        "Imprimer le résultat d'un calcul dynamique en variables généralisées au format RESULTAT"
    ),
    FORMAT=SIMP(statut="f", typ="TXM", defaut="RESULTAT", into=("RESULTAT",)),
    UNITE=SIMP(statut="f", typ=UnitType(), defaut=8, inout="out"),
    GENE=FACT(
        statut="o",
        max="**",
        regles=(
            EXCLUS(
                "TOUT_ORDRE",
                "NUME_ORDRE",
                "INST",
                "FREQ",
                "NUME_MODE",
                "LIST_INST",
                "LIST_FREQ",
                "TOUT_MODE",
                "TOUT_INST",
                "LIST_ORDRE",
            ),
            EXCLUS(
                "TOUT_MODE",
                "NUME_ORDRE",
                "INST",
                "FREQ",
                "NUME_MODE",
                "LIST_INST",
                "LIST_FREQ",
                "TOUT_ORDRE",
                "TOUT_INST",
                "LIST_ORDRE",
            ),
            EXCLUS(
                "TOUT_INST",
                "NUME_ORDRE",
                "INST",
                "FREQ",
                "NUME_MODE",
                "LIST_INST",
                "LIST_FREQ",
                "TOUT_ORDRE",
                "LIST_ORDRE",
            ),
            EXCLUS("TOUT_CMP_GENE", "NUME_CMP_GENE"),
            EXCLUS("TOUT_CHAM", "NOM_CHAM"),
            EXCLUS("TOUT_PARA", "NOM_PARA"),
        ),
        #  faut-il faire des blocs selon le type de RESU_GENE
        RESU_GENE=SIMP(statut="o", typ=(vect_asse_gene, tran_gene, mode_gene, harm_gene)),
        TOUT_ORDRE=SIMP(statut="f", typ="TXM", into=("OUI",)),
        NUME_ORDRE=SIMP(statut="f", typ="I", validators=NoRepeat(), max="**"),
        LIST_ORDRE=SIMP(statut="f", typ=listis_sdaster),
        INST=SIMP(statut="f", typ="R", validators=NoRepeat(), max="**"),
        LIST_INST=SIMP(statut="f", typ=listr8_sdaster),
        TOUT_INST=SIMP(statut="f", typ="TXM", into=("OUI",)),
        FREQ=SIMP(statut="f", typ="R", validators=NoRepeat(), max="**"),
        LIST_FREQ=SIMP(statut="f", typ=listr8_sdaster),
        TOUT_MODE=SIMP(statut="f", typ="TXM", into=("OUI",)),
        NUME_MODE=SIMP(statut="f", typ="I", validators=NoRepeat(), max="**"),
        CRITERE=SIMP(statut="f", typ="TXM", defaut="RELATIF", into=("RELATIF", "ABSOLU")),
        b_prec_rela=BLOC(
            condition="""(equal_to("CRITERE", 'RELATIF'))""",
            PRECISION=SIMP(statut="f", typ="R", defaut=1.0e-6),
        ),
        b_prec_abso=BLOC(
            condition="""(equal_to("CRITERE", 'ABSOLU'))""", PRECISION=SIMP(statut="o", typ="R")
        ),
        TOUT_CMP_GENE=SIMP(statut="f", typ="TXM", into=("OUI", "NON")),
        NUME_CMP_GENE=SIMP(statut="f", typ="I", max="**"),
        TOUT_CHAM=SIMP(statut="f", typ="TXM", into=("OUI", "NON")),
        NOM_CHAM=SIMP(
            statut="f", typ="TXM", validators=NoRepeat(), max="**", into=C_NOM_CHAM_INTO()
        ),
        TOUT_PARA=SIMP(statut="f", typ="TXM", into=("OUI", "NON")),
        NOM_PARA=SIMP(statut="f", typ="TXM", max="**"),
        SOUS_TITRE=SIMP(statut="f", typ="TXM"),
        INFO_CMP_GENE=SIMP(statut="f", typ="TXM", into=("OUI", "NON")),
        INFO_GENE=SIMP(statut="f", typ="TXM", into=("OUI", "NON")),
    ),
)
