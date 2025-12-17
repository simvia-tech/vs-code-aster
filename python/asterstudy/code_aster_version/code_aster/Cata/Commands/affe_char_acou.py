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

from ..Commons import *
from ..Language.DataStructure import *
from ..Language.Syntax import *

AFFE_CHAR_ACOU = OPER(
    nom="AFFE_CHAR_ACOU",
    op=68,
    sd_prod=char_acou,
    fr=tr("Affectation de charges et conditions aux limites acoustiques constantes"),
    reentrant="n",
    regles=(AU_MOINS_UN("PRES_IMPO", "VITE_FACE", "LIAISON_UNIF"),),
    MODELE=SIMP(statut="o", typ=modele_sdaster),
    DOUBLE_LAGRANGE=SIMP(statut="f", typ="TXM", into=("OUI",), defaut="OUI"),
    PRES_IMPO=FACT(
        statut="f",
        max="**",
        regles=(AU_MOINS_UN("TOUT", "GROUP_MA", "GROUP_NO"),),
        TOUT=SIMP(statut="f", typ="TXM", into=("OUI",)),
        GROUP_NO=SIMP(statut="f", typ=grno, validators=NoRepeat(), max="**"),
        GROUP_MA=SIMP(statut="f", typ=grma, validators=NoRepeat(), max="**"),
        SANS_GROUP_MA=SIMP(statut="f", typ=grma, validators=NoRepeat(), max="**"),
        SANS_GROUP_NO=SIMP(statut="f", typ=grno, validators=NoRepeat(), max="**"),
        PRES=SIMP(statut="o", typ="C"),
    ),
    VITE_FACE=FACT(
        statut="f",
        max="**",
        regles=(UN_PARMI("VNOR", "DIRECTION"),),
        GROUP_MA=SIMP(statut="o", typ=grma, validators=NoRepeat(), max="**"),
        VNOR=SIMP(statut="o", typ="C"),
    ),
    LIAISON_UNIF=FACT(
        statut="f",
        max="**",
        regles=(UN_PARMI("GROUP_NO", "GROUP_MA"),),
        GROUP_NO=SIMP(statut="f", typ=grno, validators=NoRepeat(), max="**"),
        GROUP_MA=SIMP(statut="f", typ=grma, validators=NoRepeat(), max="**"),
        DDL=SIMP(statut="o", typ="TXM", max=1, into=("PRES",)),
    ),
)
