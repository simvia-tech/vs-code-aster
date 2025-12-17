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

# person_in_charge: j-pierre.lefebvre at edf.fr

from ..Commons import *
from ..Language.DataStructure import *
from ..Language.Syntax import *


def extr_resu_prod(RESULTAT, **args):
    if args.get("__all__"):
        return (
            evol_elas,
            dyna_trans,
            dyna_harmo,
            acou_harmo,
            mode_meca,
            mode_acou,
            evol_ther,
            evol_noli,
            evol_varc,
            mult_elas,
            fourier_elas,
            fourier_ther,
        )

    return AsType(RESULTAT)


EXTR_RESU = OPER(
    nom="EXTR_RESU",
    op=176,
    sd_prod=extr_resu_prod,
    reentrant="f:RESULTAT",
    fr=tr("Extraire des champs au sein d'une SD Résultat"),
    reuse=SIMP(statut="c", typ=CO),
    RESULTAT=SIMP(
        statut="o",
        typ=(
            evol_elas,
            dyna_trans,
            dyna_harmo,
            acou_harmo,
            mode_meca,
            mode_acou,
            evol_ther,
            evol_noli,
            evol_varc,
            mult_elas,
            fourier_elas,
            fourier_ther,
        ),
    ),
    ARCHIVAGE=FACT(
        statut="f",
        regles=(
            UN_PARMI(
                "NUME_ORDRE",
                "INST",
                "FREQ",
                "NUME_MODE",
                "NOEUD_CMP",
                "LIST_INST",
                "LIST_FREQ",
                "LIST_ORDRE",
                "NOM_CAS",
                "LIST_ARCH",
                "PAS_ARCH",
            ),
            EXCLUS("CHAM_EXCLU", "NOM_CHAM"),
        ),
        CHAM_EXCLU=SIMP(statut="f", typ="TXM", validators=NoRepeat(), max="**"),
        NOM_CHAM=SIMP(
            statut="f", typ="TXM", validators=NoRepeat(), max="**", into=C_NOM_CHAM_INTO()
        ),
        CRITERE=SIMP(statut="f", typ="TXM", defaut="RELATIF", into=("RELATIF", "ABSOLU")),
        b_prec_rela=BLOC(
            condition="""(equal_to("CRITERE", 'RELATIF'))""",
            PRECISION=SIMP(statut="f", typ="R", defaut=1.0e-6),
        ),
        b_prec_abso=BLOC(
            condition="""(equal_to("CRITERE", 'ABSOLU'))""", PRECISION=SIMP(statut="o", typ="R")
        ),
        LIST_ARCH=SIMP(statut="f", typ=listis_sdaster),
        PAS_ARCH=SIMP(statut="f", typ="I"),
        NUME_ORDRE=SIMP(statut="f", typ="I", validators=NoRepeat(), max="**"),
        LIST_ORDRE=SIMP(statut="f", typ=listis_sdaster),
        INST=SIMP(statut="f", typ="R", validators=NoRepeat(), max="**"),
        LIST_INST=SIMP(statut="f", typ=listr8_sdaster),
        FREQ=SIMP(statut="f", typ="R", validators=NoRepeat(), max="**"),
        LIST_FREQ=SIMP(statut="f", typ=listr8_sdaster),
        NUME_MODE=SIMP(statut="f", typ="I", validators=NoRepeat(), max="**"),
        NOEUD_CMP=SIMP(statut="f", typ="TXM", validators=NoRepeat(), max="**"),
        NOM_CAS=SIMP(statut="f", typ="TXM"),
    ),
    RESTREINT=FACT(
        statut="f",
        max=1,
        fr=tr("Pour réduire une ou plusieurs sd_resultat sur un maillage ou un modèle réduit"),
        regles=(UN_PARMI("MAILLAGE", "MODELE"),),
        MAILLAGE=SIMP(statut="f", typ=maillage_sdaster),
        MODELE=SIMP(statut="f", typ=modele_sdaster),
        CHAM_MATER=SIMP(
            statut="f",
            typ=cham_mater,
            fr=tr(
                "le CHAM_MATER est nécessaire, sauf si le modèle ne contient que des éléments discrets (modélisations DIS_XXX)"
            ),
        ),
        CARA_ELEM=SIMP(
            statut="f",
            typ=cara_elem,
            fr=tr(
                "le CARA_ELEM est nécessaire dès que le modèle contient des éléments de structure : coques, poutres, ..."
            ),
        ),
    ),
    TITRE=SIMP(statut="f", typ="TXM"),
    INFO=SIMP(statut="f", typ="I", into=(1, 2), defaut=1),
)
