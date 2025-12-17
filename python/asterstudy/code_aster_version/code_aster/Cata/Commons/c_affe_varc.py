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
#
from ..Language.DataStructure import *
from ..Language.Syntax import *


def C_AFFE_VARC():
    return FACT(
        statut="f",
        max="**",
        regles=(EXCLUS("GROUP_MA", "TOUT"), UN_PARMI("EVOL", "CHAM_GD")),
        TOUT=SIMP(statut="f", typ="TXM", into=("OUI",)),
        GROUP_MA=SIMP(statut="f", typ=grma, validators=NoRepeat(), max="**"),
        NOM_VARC=SIMP(
            statut="o",
            typ="TXM",
            into=(
                "TEMP",
                "GEOM",
                "CORR",
                "IRRA",
                "HYDR",
                "SECH",
                "EPSA",
                "M_ACIER",
                "M_ZIRC",
                "NEUT1",
                "NEUT2",
                "NEUT3",
                "PTOT",
            ),
        ),
        CHAM_GD=SIMP(statut="f", typ=cham_gd_sdaster),
        EVOL=SIMP(statut="f", typ=evol_sdaster),
        B_EVOL=BLOC(
            condition="""exists("EVOL")""",
            NOM_CHAM=SIMP(
                statut="f",
                typ="TXM",
                into=(
                    "TEMP",
                    "CORR",
                    "IRRA",
                    "NEUT",
                    "GEOM",
                    "HYDR_ELNO",
                    "HYDR_NOEU",
                    "META_ELNO",
                    "META_NOEU",
                    "EPSA_ELNO",
                    "EPSA_NOEU",
                    "PTOT",
                    "HHO_TEMP",
                ),
            ),
            PROL_DROITE=SIMP(
                statut="f", typ="TXM", defaut="EXCLU", into=("CONSTANT", "LINEAIRE", "EXCLU")
            ),
            PROL_GAUCHE=SIMP(
                statut="f", typ="TXM", defaut="EXCLU", into=("CONSTANT", "LINEAIRE", "EXCLU")
            ),
            FONC_INST=SIMP(statut="f", typ=(fonction_sdaster, formule)),
        ),
        # VALE_REF est nécessaire pour certaines VARC :
        B_VALE_REF=BLOC(
            condition="""is_in("NOM_VARC", ('TEMP','SECH'))""", VALE_REF=SIMP(statut="o", typ="R")
        ),
    )


C_AFFE_VARC_EXTE = FACT(statut="o", AFFE_VARC=C_AFFE_VARC())
