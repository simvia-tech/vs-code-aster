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

POST_GENE_PHYS = OPER(
    nom="POST_GENE_PHYS",
    op=58,
    sd_prod=table_sdaster,
    fr="Post-traiter dans la base physique des résultats dyanmiques en coordonnées généralisées",
    reentrant="n",
    RESU_GENE=SIMP(statut="o", typ=(tran_gene, harm_gene)),
    MODE_MECA=SIMP(statut="f", typ=mode_meca),
    OBSERVATION=FACT(
        statut="o",
        min=1,
        max="**",
        regles=(
            EXCLUS(
                "INST", "LIST_INST", "TOUT_INST", "NUME_ORDRE", "TOUT_ORDRE", "FREQ", "LIST_FREQ"
            ),
            EXCLUS("NOEUD", "GROUP_NO", "MAILLE", "GROUP_MA"),
            AU_MOINS_UN("NOEUD", "GROUP_NO", "MAILLE", "GROUP_MA"),
        ),
        NOM_CHAM=SIMP(
            statut="f",
            typ="TXM",
            validators=NoRepeat(),
            max=1,
            defaut="DEPL",
            into=(
                "DEPL",
                "VITE",
                "ACCE",
                "DEPL_ABSOLU",
                "VITE_ABSOLU",
                "ACCE_ABSOLU",
                "FORC_NODA",
                "EFGE_ELNO",
                "SIPO_ELNO",
                "SIGM_ELNO",
                "EFGE_ELGA",
                "SIGM_ELGA",
            ),
        ),
        NOM_CMP=SIMP(statut="f", typ="TXM", max=20),
        INST=SIMP(statut="f", typ="R", validators=NoRepeat(), max="**"),
        TOUT_INST=SIMP(statut="f", typ="TXM", into=("OUI",)),
        LIST_INST=SIMP(statut="f", typ=listr8_sdaster),
        NUME_ORDRE=SIMP(statut="f", typ="I", validators=NoRepeat(), max="**"),
        TOUT_ORDRE=SIMP(statut="f", typ="TXM", into=("OUI",)),
        FREQ=SIMP(statut="f", typ="R", validators=NoRepeat(), max="**"),
        LIST_FREQ=SIMP(statut="f", typ=listr8_sdaster),
        b_prec=BLOC(
            condition="""(exists("INST")) or (exists("LIST_INST")) or (exists("FREQ")) or (exists("LIST_FREQ"))""",
            CRITERE=SIMP(statut="f", typ="TXM", defaut="RELATIF", into=("ABSOLU", "RELATIF")),
            b_prec_rela=BLOC(
                condition="""(equal_to("CRITERE", 'RELATIF'))""",
                PRECISION=SIMP(statut="f", typ="R", defaut=1.0e-6),
            ),
            b_prec_abso=BLOC(
                condition="""(equal_to("CRITERE", 'ABSOLU'))""", PRECISION=SIMP(statut="o", typ="R")
            ),
        ),
        NOEUD=SIMP(statut="c", typ=no, validators=NoRepeat(), max="**"),
        GROUP_NO=SIMP(statut="f", typ=grno, validators=NoRepeat(), max="**"),
        MAILLE=SIMP(statut="c", typ=ma, validators=NoRepeat(), max="**"),
        GROUP_MA=SIMP(statut="f", typ=grma, validators=NoRepeat(), max="**"),
        b_acce_abs=BLOC(
            condition="""(equal_to("NOM_CHAM", 'ACCE_ABSOLU'))""",
            regles=(PRESENT_PRESENT("ACCE_MONO_APPUI", "DIRECTION"),),
            ACCE_MONO_APPUI=SIMP(statut="f", typ=(fonction_sdaster, nappe_sdaster, formule), max=3),
            DIRECTION=SIMP(statut="f", typ="R", min=3, max=9),
        ),
    ),
    TITRE=SIMP(statut="f", typ="TXM"),
)
