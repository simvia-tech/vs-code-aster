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


def crea_table_prod(TYPE_TABLE, **args):
    """Typage du concept résultat"""
    if args.get("__all__"):
        return (table_fonction, table_container, table_sdaster)

    if TYPE_TABLE == "TABLE_FONCTION":
        return table_fonction
    elif TYPE_TABLE == "TABLE_CONTAINER":
        return table_container
    else:
        return table_sdaster


CREA_TABLE = OPER(
    nom="CREA_TABLE",
    op=36,
    sd_prod=crea_table_prod,
    fr=tr("Création d'une table à partir d'une fonction ou de deux listes"),
    reentrant="n",
    regles=(EXCLUS("FONCTION", "LISTE", "RESU"),),
    LISTE=FACT(
        statut="f",
        max="**",
        fr=tr("Creation d'une table a partir de listes"),
        regles=(UN_PARMI("LISTE_I", "LISTE_R", "LISTE_K", "LISTE_CO"),),
        b_liste_irk=BLOC(condition=""" not exists("LISTE_CO")""", PARA=SIMP(statut="o", typ="TXM")),
        TYPE_K=SIMP(statut="f", typ="TXM", defaut="K8", into=("K8", "K16", "K24")),
        NUME_LIGN=SIMP(statut="f", typ="I", max="**"),
        LISTE_I=SIMP(statut="f", typ="I", max="**"),
        LISTE_R=SIMP(statut="f", typ="R", max="**"),
        LISTE_K=SIMP(statut="f", typ="TXM", max="**"),
        LISTE_CO=SIMP(
            statut="f",
            typ=(
                matr_asse_gene_r,
                matr_elem_depl_r,
                vect_elem_depl_r,
                matr_elem_temp_r,
                vect_elem_temp_r,
                cham_gd_sdaster,
                cham_no_sdaster,
                carte_sdaster,
                cham_elem,
                mode_meca,
                table_sdaster,
                fonction_sdaster,
                fonction_c,
                nappe_sdaster,
            ),
            max="**",
        ),
    ),
    FONCTION=FACT(
        statut="f",
        fr=tr("Creation d'une table a partir d'une fonction"),
        FONCTION=SIMP(statut="o", typ=(fonction_c, fonction_sdaster)),
        PARA=SIMP(statut="f", typ="TXM", min=2, max=2),
    ),
    RESU=FACT(
        statut="f",
        max=1,
        fr=tr("Creation d'une table a partir d'un resultat ou d'un champ"),
        regles=(
            UN_PARMI("CHAM_GD", "RESULTAT"),
            UN_PARMI("TOUT_CMP", "NOM_CMP", "NOM_VARI"),
            PRESENT_ABSENT("TOUT", "GROUP_MA", "GROUP_NO"),
            AU_MOINS_UN("TOUT", "GROUP_MA", "GROUP_NO"),
        ),
        CHAM_GD=SIMP(statut="f", typ=cham_gd_sdaster),
        RESULTAT=SIMP(statut="f", typ=resultat_sdaster),
        INTITULE=SIMP(statut="f", typ="TXM", defaut=" "),
        b_resultat=BLOC(
            condition="""exists('RESULTAT')""",
            regles=(
                EXCLUS(
                    "TOUT_ORDRE",
                    "NUME_ORDRE",
                    "LIST_ORDRE",
                    "INST",
                    "LIST_INST",
                    "MODE",
                    "LIST_MODE",
                    "FREQ",
                    "LIST_FREQ",
                ),
            ),
            NOM_CHAM=SIMP(statut="o", typ="TXM", validators=NoRepeat(), into=C_NOM_CHAM_INTO()),
            TOUT_ORDRE=SIMP(statut="f", typ="TXM", into=("OUI",)),
            NUME_ORDRE=SIMP(statut="f", typ="I", max="**"),
            LIST_ORDRE=SIMP(statut="f", typ=listis_sdaster),
            INST=SIMP(statut="f", typ="R", max="**"),
            LIST_INST=SIMP(statut="f", typ=listr8_sdaster),
            MODE=SIMP(statut="f", typ="I", max="**"),
            LIST_MODE=SIMP(statut="f", typ=listis_sdaster),
            FREQ=SIMP(statut="f", typ="R", max="**"),
            LIST_FREQ=SIMP(statut="f", typ=listr8_sdaster),
            CRITERE=SIMP(statut="f", typ="TXM", defaut="RELATIF", into=("RELATIF", "ABSOLU")),
            b_prec_rela=BLOC(
                condition="""equal_to('CRITERE', 'RELATIF')""",
                PRECISION=SIMP(statut="f", typ="R", defaut=1.0e-6),
            ),
            b_prec_abso=BLOC(
                condition="""equal_to('CRITERE', 'ABSOLU')""", PRECISION=SIMP(statut="o", typ="R")
            ),
        ),
        b_cham_gd=BLOC(
            condition="""exists('CHAM_GD')""", CARA_ELEM=SIMP(statut="f", typ=cara_elem)
        ),
        TOUT_CMP=SIMP(statut="f", typ="TXM", into=("OUI",)),
        NOM_CMP=SIMP(statut="f", typ="TXM", max="**"),
        NOM_VARI=SIMP(statut="f", typ="TXM", max="**"),
        TOUT=SIMP(statut="f", typ="TXM", into=("OUI",)),
        GROUP_MA=SIMP(statut="f", typ=grma, validators=NoRepeat(), max="**"),
        GROUP_NO=SIMP(statut="f", typ=grno, validators=NoRepeat(), max="**"),
    ),
    TYPE_TABLE=SIMP(
        statut="f", typ="TXM", defaut="TABLE", into=("TABLE", "TABLE_FONCTION", "TABLE_CONTAINER")
    ),
    TITRE=SIMP(statut="f", typ="TXM"),
)
