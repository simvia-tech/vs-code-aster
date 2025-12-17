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

# person_in_charge: mathieu.courtois at edf.fr

from ..Commons import *
from ..Language.DataStructure import *
from ..Language.Syntax import *

TEST_RESU = PROC(
    nom="TEST_RESU",
    op=23,
    fr=tr(
        "Extraction d'une valeur d'une structure de donnée et comparaison à une valeur de référence"
    ),
    regles=(
        AU_MOINS_UN(
            "CHAM_NO", "CHAM_ELEM", "CARTE", "RESU", "GENE", "OBJET", "TEST_NAN", "MAILLAGE"
        )
    ),
    CHAM_NO=FACT(
        statut="f",
        max="**",
        regles=(PRESENT_PRESENT("GROUP_NO", "NOM_CMP"),),
        CHAM_GD=SIMP(statut="o", typ=cham_no_sdaster),
        GROUP_NO=SIMP(statut="f", typ=grno),
        NOM_CMP=SIMP(statut="f", typ="TXM", max=1),
        **C_TEST_REFERENCE("CHAM_NO", max="**")
    ),
    CARTE=FACT(
        statut="f",
        max="**",
        CHAM_GD=SIMP(statut="o", typ=carte_sdaster),
        GROUP_MA=SIMP(statut="f", typ=grma),
        NOM_CMP=SIMP(statut="o", typ="TXM", max=1),
        **C_TEST_REFERENCE("CARTE", max=1)
    ),
    CHAM_ELEM=FACT(
        statut="f",
        max="**",
        regles=(  # UN_PARMI('GROUP_MA','TYPE_TEST',) dans trchel.f
            EXCLUS("GROUP_NO", "POINT"),
            PRESENT_PRESENT("GROUP_NO", "NOM_CMP"),
            PRESENT_PRESENT("POINT", "NOM_CMP"),
        ),
        CHAM_GD=SIMP(statut="o", typ=cham_elem),
        GROUP_MA=SIMP(statut="f", typ=grma),
        POINT=SIMP(statut="f", typ="I"),
        SOUS_POINT=SIMP(statut="f", typ="I"),
        GROUP_NO=SIMP(statut="f", typ=grno),
        NOM_CMP=SIMP(statut="f", typ="TXM", max=1),
        **C_TEST_REFERENCE("CHAM_ELEM", max="**")
    ),
    RESU=FACT(
        statut="f",
        max="**",
        regles=(
            UN_PARMI("NUME_ORDRE", "INST", "FREQ", "NUME_MODE", "NOEUD_CMP", "NOM_CAS", "ANGLE"),
            UN_PARMI("NOM_CHAM", "PARA"),
            PRESENT_ABSENT("PARA", "GROUP_MA", "GROUP_NO", "POINT", "NOM_CMP", "NOM_VARI"),
            EXCLUS("GROUP_NO", "POINT"),  # EXCLUS avec 'TYPE_TEST' dans trresu.f
            EXCLUS("NOM_CMP", "NOM_VARI"),
        ),
        RESULTAT=SIMP(statut="o", typ=resultat_sdaster),
        NUME_ORDRE=SIMP(statut="f", typ="I"),
        INST=SIMP(statut="f", typ="R"),
        FREQ=SIMP(statut="f", typ="R"),
        NUME_MODE=SIMP(statut="f", typ="I"),
        NOEUD_CMP=SIMP(statut="f", typ="TXM", min=2, max=2),
        NOM_CAS=SIMP(statut="f", typ="TXM"),
        ANGLE=SIMP(statut="f", typ="R"),
        PARA=SIMP(statut="f", typ="TXM"),
        NOM_CHAM=SIMP(statut="f", typ="TXM", validators=NoRepeat(), into=C_NOM_CHAM_INTO()),
        NOM_CMP=SIMP(statut="f", typ="TXM", max=1),
        NOM_VARI=SIMP(statut="f", typ="TXM", max=1),
        GROUP_MA=SIMP(statut="f", typ=grma),
        GROUP_NO=SIMP(statut="f", typ=grno, max="**"),
        POINT=SIMP(statut="f", typ="I"),
        SOUS_POINT=SIMP(statut="f", typ="I"),
        **C_TEST_REFERENCE("RESU", max="**")
    ),
    GENE=FACT(
        statut="f",
        max="**",
        RESU_GENE=SIMP(statut="o", typ=(vect_asse_gene, tran_gene, mode_gene, harm_gene)),
        b_vect_asse=BLOC(
            condition="""is_type("RESU_GENE") == vect_asse_gene""",
            NUME_CMP_GENE=SIMP(statut="o", typ="I"),
        ),
        b_mode=BLOC(
            condition="""is_type("RESU_GENE") == mode_gene""",
            regles=(
                UN_PARMI("NUME_ORDRE", "FREQ", "NUME_MODE"),
                UN_PARMI("NOM_CHAM", "PARA"),
                PRESENT_PRESENT("NOM_CHAM", "NUME_CMP_GENE"),
            ),
            NOM_CHAM=SIMP(statut="f", typ="TXM", validators=NoRepeat(), into=C_NOM_CHAM_INTO()),
            NUME_CMP_GENE=SIMP(statut="f", typ="I"),
            PARA=SIMP(statut="f", typ="TXM"),
            NUME_ORDRE=SIMP(statut="f", typ="I"),
            NUME_MODE=SIMP(statut="f", typ="I"),
            FREQ=SIMP(statut="f", typ="R"),
        ),
        b_harm=BLOC(
            condition="""is_type("RESU_GENE") == harm_gene""",
            regles=(UN_PARMI("NUME_ORDRE", "FREQ"),),
            NOM_CHAM=SIMP(statut="o", typ="TXM", validators=NoRepeat(), into=C_NOM_CHAM_INTO()),
            NUME_CMP_GENE=SIMP(statut="o", typ="I"),
            NUME_ORDRE=SIMP(statut="f", typ="I"),
            FREQ=SIMP(statut="f", typ="R"),
        ),
        b_tran=BLOC(
            condition="""is_type("RESU_GENE") == tran_gene""",
            regles=(UN_PARMI("NUME_ORDRE", "INST"),),
            NOM_CHAM=SIMP(statut="o", typ="TXM", validators=NoRepeat(), into=C_NOM_CHAM_INTO()),
            NUME_CMP_GENE=SIMP(statut="o", typ="I"),
            NUME_ORDRE=SIMP(statut="f", typ="I"),
            INST=SIMP(statut="f", typ="R"),
        ),
        **C_TEST_REFERENCE("GENE", max="**")
    ),
    OBJET=FACT(
        statut="f", max="**", NOM=SIMP(statut="o", typ="TXM"), **C_TEST_REFERENCE("OBJET", max=1)
    ),
    MAILLAGE=FACT(
        statut="f",
        max="**",
        MAILLAGE=SIMP(statut="o", typ=maillage_sdaster),
        CARA=SIMP(
            statut="o",
            typ="TXM",
            max=1,
            into=(
                "NB_MAILLE",
                "NB_NOEUD",
                "NB_GROUP_MA",
                "NB_GROUP_NO",
                "NB_MA_GROUP_MA",
                "NB_NO_GROUP_NO",
            ),
        ),
        NOM_GROUP_MA=SIMP(statut="f", typ=grma, max=1),
        NOM_GROUP_NO=SIMP(statut="f", typ=grno, max=1),
        **C_TEST_REFERENCE("MAILLAGE", max=1)
    ),
    TEST_NAN=SIMP(statut="f", typ="TXM", into=("OUI", "NON")),
)
