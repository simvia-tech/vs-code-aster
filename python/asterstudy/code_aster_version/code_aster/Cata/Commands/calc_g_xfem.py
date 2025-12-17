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

# person_in_charge: samuel.geniaut at edf.fr

from ..Commons import *
from ..Language.DataStructure import *
from ..Language.Syntax import *


CALC_G_XFEM = OPER(
    nom="CALC_G_XFEM",
    op=100,
    sd_prod=table_container,
    fr=tr(
        "Calcul du taux de restitution d'énergie par la méthode theta en thermo-élasticité"
        " et les facteurs d'intensité de contraintes."
    ),
    reentrant="n",
    CHAM_THETA=SIMP(statut="f", typ=CO, max=1),
    THETA=FACT(
        statut="o",
        FISSURE=SIMP(statut="o", typ=fiss_xfem, max=1),
        NB_POINT_FOND=SIMP(statut="f", typ="I", val_min=2),
        regles=(PRESENT_PRESENT("R_INF", "R_SUP"), PRESENT_PRESENT("R_INF_FO", "R_SUP_FO")),
        NUME_FOND=SIMP(statut="f", typ="I", defaut=1),
        R_INF=SIMP(statut="f", typ="R"),
        R_SUP=SIMP(statut="f", typ="R"),
        R_INF_FO=SIMP(statut="f", typ=(fonction_sdaster, nappe_sdaster, formule)),
        R_SUP_FO=SIMP(statut="f", typ=(fonction_sdaster, nappe_sdaster, formule)),
        DIRECTION=SIMP(statut="f", typ="R", max=2, min=2),
    ),
    RESULTAT=SIMP(statut="o", typ=(evol_elas, evol_noli, dyna_trans, mode_meca)),
    regles=(
        EXCLUS(
            "TOUT_ORDRE",
            "NUME_ORDRE",
            "LIST_ORDRE",
            "INST",
            "LIST_INST",
            "TOUT_MODE",
            "NUME_MODE",
            "LIST_MODE",
            "FREQ",
            "LIST_FREQ",
        ),
    ),
    TOUT_ORDRE=SIMP(statut="f", typ="TXM", into=("OUI",)),
    NUME_ORDRE=SIMP(statut="f", typ="I", validators=NoRepeat(), max="**"),
    LIST_ORDRE=SIMP(statut="f", typ=listis_sdaster),
    INST=SIMP(statut="f", typ="R", validators=NoRepeat(), max="**"),
    LIST_INST=SIMP(statut="f", typ=listr8_sdaster),
    TOUT_MODE=SIMP(statut="f", typ="TXM", into=("OUI",)),
    NUME_MODE=SIMP(statut="f", typ="I", validators=NoRepeat(), max="**"),
    LIST_MODE=SIMP(statut="f", typ=listis_sdaster),
    LIST_FREQ=SIMP(statut="f", typ=listr8_sdaster),
    FREQ=SIMP(statut="f", typ="R", validators=NoRepeat(), max="**"),
    b_acce_reel=BLOC(
        condition="""(exists("INST"))or(exists("LIST_INST"))or(exists("FREQ"))or(exists("LIST_FREQ"))""",
        CRITERE=SIMP(statut="f", typ="TXM", defaut="RELATIF", into=("RELATIF", "ABSOLU")),
        b_prec_rela=BLOC(
            condition="""(equal_to("CRITERE", 'RELATIF'))""",
            PRECISION=SIMP(statut="f", typ="R", defaut=1.0e-6),
        ),
        b_prec_abso=BLOC(
            condition="""(equal_to("CRITERE", 'ABSOLU'))""", PRECISION=SIMP(statut="o", typ="R")
        ),
    ),
    EXCIT=FACT(
        statut="f",
        max="**",
        CHARGE=SIMP(statut="f", typ=(char_meca, char_cine_meca)),
        FONC_MULT=SIMP(statut="f", typ=(fonction_sdaster, nappe_sdaster, formule)),
        TYPE_CHARGE=SIMP(statut="f", typ="TXM", defaut="FIXE_CSTE", into=("FIXE_CSTE",)),
    ),
    COMPORTEMENT=FACT(
        statut="f",
        RELATION=SIMP(statut="o", typ="TXM", into=C_RELATION("CALC_G_XFEM")),
        DEFORMATION=SIMP(statut="f", typ="TXM", defaut="PETIT", into=("PETIT", "PETIT_REAC")),
        regles=(PRESENT_ABSENT("TOUT", "GROUP_MA", "MAILLE"),),
        TOUT=SIMP(statut="f", typ="TXM", into=("OUI",)),
        GROUP_MA=SIMP(statut="f", typ=grma, validators=NoRepeat(), max="**"),
        MAILLE=SIMP(statut="c", typ=ma, validators=NoRepeat(), max="**"),
    ),
    ETAT_INIT=FACT(
        statut="f",
        SIGM=SIMP(statut="o", typ=(cham_no_sdaster, cham_elem)),
        #           DEPL            =SIMP(statut='f',typ=cham_no_sdaster),
    ),
    LISSAGE=FACT(
        statut="d",
        LISSAGE_THETA=SIMP(statut="f", typ="TXM", defaut="LEGENDRE", into=("LEGENDRE", "LAGRANGE")),
        LISSAGE_G=SIMP(
            statut="f",
            typ="TXM",
            defaut="LEGENDRE",
            into=("LEGENDRE", "LAGRANGE", "LAGRANGE_NO_NO"),
        ),
        b_legen=BLOC(
            condition="""(equal_to("LISSAGE_THETA", 'LEGENDRE')) or (equal_to("LISSAGE_G", 'LEGENDRE'))""",
            DEGRE=SIMP(statut="f", typ="I", defaut=5, into=(0, 1, 2, 3, 4, 5, 6, 7)),
        ),
    ),
    OPTION=SIMP(statut="f", typ="TXM", max=1, defaut="CALC_G", into=("CALC_G", "CALC_K_G")),
    b_cal_contrainte=BLOC(
        condition="""(exists("COMPORTEMENT") and (equal_to("OPTION", 'CALC_G')))""",
        CALCUL_CONTRAINTE=SIMP(statut="f", typ="TXM", defaut="OUI", into=("OUI", "NON")),
    ),
    TITRE=SIMP(statut="f", typ="TXM"),
    INFO=SIMP(statut="f", typ="I", defaut=1, into=(1, 2)),
)
