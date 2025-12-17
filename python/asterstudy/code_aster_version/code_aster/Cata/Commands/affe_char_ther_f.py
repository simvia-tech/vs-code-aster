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

# person_in_charge: mickael.abbas at edf.fr

from ..Commons import *
from ..Language.DataStructure import *
from ..Language.Syntax import *

AFFE_CHAR_THER_F = OPER(
    nom="AFFE_CHAR_THER_F",
    op=34,
    sd_prod=char_ther,
    fr=tr(
        "Affectation de charges et conditions aux limites thermiques fonction d'un (ou plusieurs)"
        " paramètres (temps, ...)"
    ),
    reentrant="n",
    regles=(
        AU_MOINS_UN(
            "TEMP_IMPO",
            "SOURCE",
            "SOUR_NL",
            "FLUX_REP",
            "FLUX_NL",
            "ECHANGE",
            "ECHANGE_PAROI",
            "LIAISON_DDL",
            "LIAISON_GROUP",
            "LIAISON_UNIF",
            "PRE_GRAD_TEMP",
            "RAYONNEMENT",
            "CONVECTION",
        ),
    ),
    MODELE=SIMP(statut="o", typ=(modele_sdaster)),
    DOUBLE_LAGRANGE=SIMP(statut="f", typ="TXM", into=("OUI", "NON"), defaut="OUI"),
    TEMP_IMPO=FACT(
        statut="f",
        max="**",
        regles=(
            AU_MOINS_UN("TOUT", "GROUP_MA", "GROUP_NO"),
            AU_MOINS_UN("TEMP", "TEMP_MIL", "TEMP_SUP", "TEMP_INF"),
        ),
        TOUT=SIMP(statut="f", typ="TXM", into=("OUI",)),
        GROUP_NO=SIMP(statut="f", typ=grno, validators=NoRepeat(), max="**"),
        GROUP_MA=SIMP(statut="f", typ=grma, validators=NoRepeat(), max="**"),
        SANS_GROUP_MA=SIMP(statut="f", typ=grma, validators=NoRepeat(), max="**"),
        SANS_GROUP_NO=SIMP(statut="f", typ=grno, validators=NoRepeat(), max="**"),
        TEMP=SIMP(statut="f", typ=(fonction_sdaster, nappe_sdaster, formule)),
        TEMP_MIL=SIMP(statut="f", typ=(fonction_sdaster, nappe_sdaster, formule)),
        TEMP_INF=SIMP(statut="f", typ=(fonction_sdaster, nappe_sdaster, formule)),
        TEMP_SUP=SIMP(statut="f", typ=(fonction_sdaster, nappe_sdaster, formule)),
    ),
    FLUX_REP=FACT(
        statut="f",
        max="**",
        regles=(
            UN_PARMI("TOUT", "GROUP_MA", TOUT="OUI"),
            AU_MOINS_UN("FLUN", "FLUN_INF", "FLUN_SUP", "FLUX_X", "FLUX_Y", "FLUX_Z"),
        ),
        TOUT=SIMP(statut="f", typ="TXM", into=("OUI",)),
        GROUP_MA=SIMP(statut="f", typ=grma, validators=NoRepeat(), max="**"),
        FLUN=SIMP(statut="f", typ=(fonction_sdaster, nappe_sdaster, formule)),
        FLUN_INF=SIMP(statut="f", typ=(fonction_sdaster, nappe_sdaster, formule)),
        FLUN_SUP=SIMP(statut="f", typ=(fonction_sdaster, nappe_sdaster, formule)),
        FLUX_X=SIMP(statut="f", typ=(fonction_sdaster, nappe_sdaster, formule)),
        FLUX_Y=SIMP(statut="f", typ=(fonction_sdaster, nappe_sdaster, formule)),
        FLUX_Z=SIMP(statut="f", typ=(fonction_sdaster, nappe_sdaster, formule)),
    ),
    FLUX_NL=FACT(
        statut="f",
        max="**",
        regles=(UN_PARMI("TOUT", "GROUP_MA", TOUT="OUI"),),
        TOUT=SIMP(statut="f", typ="TXM", into=("OUI",)),
        GROUP_MA=SIMP(statut="f", typ=grma, validators=NoRepeat(), max="**"),
        FLUN=SIMP(statut="o", typ=(fonction_sdaster,)),
    ),
    RAYONNEMENT=FACT(
        statut="f",
        max="**",
        fr=tr("Attention, exprimer les températures en Celsius si rayonnement"),
        regles=(UN_PARMI("TOUT", "GROUP_MA", TOUT="OUI"),),
        TOUT=SIMP(statut="f", typ="TXM", into=("OUI",)),
        GROUP_MA=SIMP(statut="f", typ=grma, validators=NoRepeat(), max="**"),
        SIGMA=SIMP(statut="o", typ=(fonction_sdaster, nappe_sdaster, formule)),
        EPSILON=SIMP(statut="o", typ=(fonction_sdaster, nappe_sdaster, formule)),
        TEMP_EXT=SIMP(statut="o", typ=(fonction_sdaster, nappe_sdaster, formule)),
    ),
    ECHANGE=FACT(
        statut="f",
        max="**",
        regles=(
            UN_PARMI("TOUT", "GROUP_MA", TOUT="OUI"),
            AU_MOINS_UN("COEF_H", "COEF_H_INF", "COEF_H_SUP"),
            ENSEMBLE("COEF_H", "TEMP_EXT"),
            ENSEMBLE("COEF_H_INF", "TEMP_EXT_INF"),
            ENSEMBLE("COEF_H_SUP", "TEMP_EXT_SUP"),
        ),
        TOUT=SIMP(statut="f", typ="TXM", into=("OUI",)),
        GROUP_MA=SIMP(statut="f", typ=grma, validators=NoRepeat(), max="**"),
        COEF_H=SIMP(statut="f", typ=(fonction_sdaster, nappe_sdaster, formule)),
        TEMP_EXT=SIMP(statut="f", typ=(fonction_sdaster, nappe_sdaster, formule)),
        COEF_H_INF=SIMP(statut="f", typ=(fonction_sdaster, nappe_sdaster, formule)),
        TEMP_EXT_INF=SIMP(statut="f", typ=(fonction_sdaster, nappe_sdaster, formule)),
        COEF_H_SUP=SIMP(statut="f", typ=(fonction_sdaster, nappe_sdaster, formule)),
        TEMP_EXT_SUP=SIMP(statut="f", typ=(fonction_sdaster, nappe_sdaster, formule)),
    ),
    SOURCE=FACT(
        statut="f",
        max="**",
        regles=(UN_PARMI("TOUT", "GROUP_MA", TOUT="OUI"),),
        TOUT=SIMP(statut="f", typ="TXM", into=("OUI",)),
        GROUP_MA=SIMP(statut="f", typ=grma, validators=NoRepeat(), max="**"),
        SOUR=SIMP(statut="o", typ=(fonction_sdaster, nappe_sdaster, formule)),
    ),
    SOUR_NL=FACT(
        statut="f",
        max="**",
        regles=(UN_PARMI("TOUT", "GROUP_MA", TOUT="OUI"),),
        TOUT=SIMP(statut="f", typ="TXM", into=("OUI",)),
        GROUP_MA=SIMP(statut="f", typ=grma, validators=NoRepeat(), max="**"),
        SOUR=SIMP(statut="o", typ=(fonction_sdaster, nappe_sdaster, formule)),
    ),
    PRE_GRAD_TEMP=FACT(
        statut="f",
        max="**",
        regles=(
            UN_PARMI("TOUT", "GROUP_MA", TOUT="OUI"),
            AU_MOINS_UN("FLUX_X", "FLUX_Y", "FLUX_Z"),
        ),
        TOUT=SIMP(statut="f", typ="TXM", into=("OUI",)),
        GROUP_MA=SIMP(statut="f", typ=grma, validators=NoRepeat(), max="**"),
        FLUX_X=SIMP(statut="f", typ=(fonction_sdaster, nappe_sdaster, formule)),
        FLUX_Y=SIMP(statut="f", typ=(fonction_sdaster, nappe_sdaster, formule)),
        FLUX_Z=SIMP(statut="f", typ=(fonction_sdaster, nappe_sdaster, formule)),
    ),
    ECHANGE_PAROI=FACT(
        statut="f",
        max="**",
        regles=(UN_PARMI("GROUP_MA_1", "FISSURE"), UN_PARMI("GROUP_MA_2", "FISSURE")),
        GROUP_MA_1=SIMP(statut="f", typ=grma, validators=NoRepeat(), max="**"),
        GROUP_MA_2=SIMP(statut="f", typ=grma, validators=NoRepeat(), max="**"),
        FISSURE=SIMP(statut="f", typ=fiss_xfem, validators=NoRepeat(), min=1, max=100),
        #          ----------------------
        b_paroi_maillee=BLOC(
            condition="""not exists("FISSURE")""",
            COEF_H=SIMP(statut="o", typ=(fonction_sdaster, nappe_sdaster, formule)),
            TRAN=SIMP(statut="f", typ="R", min=2, max=3),
        ),
        #          ----------------------
        b_xfem=BLOC(
            condition="""exists("FISSURE")""",
            regles=(UN_PARMI("COEF_H", "TEMP_CONTINUE"),),
            COEF_H=SIMP(statut="f", typ=(fonction_sdaster, nappe_sdaster, formule)),
            TEMP_CONTINUE=SIMP(statut="f", typ="TXM", into=("OUI",)),
        ),
    ),
    LIAISON_DDL=FACT(
        statut="f",
        max="**",
        GROUP_NO=SIMP(statut="f", typ=grno, max="**"),
        DDL=SIMP(statut="f", typ="TXM", max="**", into=C_NOM_DDL_INTO("THERMIQUE")),
        COEF_MULT=SIMP(statut="o", typ="R", max="**"),
        COEF_IMPO=SIMP(statut="o", typ=(fonction_sdaster, nappe_sdaster, formule)),
    ),
    LIAISON_GROUP=FACT(
        statut="f",
        max="**",
        regles=(
            UN_PARMI("GROUP_MA_1", "GROUP_NO_1"),
            UN_PARMI("GROUP_MA_2", "GROUP_NO_2"),
            EXCLUS("GROUP_MA_1", "GROUP_NO_2"),
            EXCLUS("GROUP_NO_1", "GROUP_MA_2"),
        ),
        GROUP_MA_1=SIMP(statut="f", typ=grma, validators=NoRepeat(), max="**"),
        GROUP_NO_1=SIMP(statut="f", typ=grno, validators=NoRepeat(), max="**"),
        GROUP_MA_2=SIMP(statut="f", typ=grma, validators=NoRepeat(), max="**"),
        GROUP_NO_2=SIMP(statut="f", typ=grno, validators=NoRepeat(), max="**"),
        SANS_GROUP_NO=SIMP(statut="f", typ=grno, validators=NoRepeat(), max="**"),
        DDL_1=SIMP(
            statut="f", typ="TXM", max="**", defaut="TEMP", into=C_NOM_DDL_INTO("THERMIQUE")
        ),
        COEF_MULT_1=SIMP(statut="o", typ="R", max="**"),
        DDL_2=SIMP(
            statut="f", typ="TXM", max="**", defaut="TEMP", into=C_NOM_DDL_INTO("THERMIQUE")
        ),
        COEF_MULT_2=SIMP(statut="o", typ="R", max="**"),
        COEF_IMPO=SIMP(statut="o", typ=(fonction_sdaster, nappe_sdaster, formule)),
        TRAN=SIMP(statut="f", typ="R", max="**"),
        ANGL_NAUT=SIMP(statut="f", typ="R", max="**"),
        CENTRE=SIMP(statut="f", typ="R", max="**"),
    ),
    LIAISON_UNIF=FACT(
        statut="f",
        max="**",
        regles=(UN_PARMI("GROUP_NO", "GROUP_MA"),),
        GROUP_NO=SIMP(statut="f", typ=grno, validators=NoRepeat(), max="**"),
        GROUP_MA=SIMP(statut="f", typ=grma, validators=NoRepeat(), max="**"),
        DDL=SIMP(
            statut="f",
            typ="TXM",
            defaut="TEMP",
            into=C_NOM_DDL_INTO("THERMIQUE"),
            max="**",
            validators=NoRepeat(),
        ),
    ),
    CONVECTION=FACT(statut="f", VITESSE=SIMP(statut="o", typ=cham_no_sdaster)),
    INFO=SIMP(statut="f", typ="I", defaut=1, into=(1, 2)),
    translation={"AFFE_CHAR_THER_F": "Assign variable thermal load"},
)
