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

# person_in_charge: sofiane.hendili at edf.fr

from ..Commons import *
from ..Language.DataStructure import *
from ..Language.Syntax import *

DEFI_TRC = OPER(
    nom="DEFI_TRC",
    op=94,
    sd_prod=table_sdaster,
    reentrant="n",
    fr=tr(
        "Définir d'un diagramme de transformations en refroidissement continu (TRC) de référence d'un acier"
        " pour les calculs métallurgiques."
    ),
    HIST_EXP=FACT(statut="o", max="**", VALE=SIMP(statut="o", typ="R", max="**")),
    TEMP_MS=FACT(
        statut="o",
        max=1,
        SEUIL=SIMP(statut="o", typ="R"),
        AKM=SIMP(statut="o", typ="R"),
        BKM=SIMP(statut="o", typ="R"),
        TPLM=SIMP(statut="o", typ="R"),
    ),
    GRAIN_AUST=FACT(statut="f", max=1, DREF=SIMP(statut="f", typ="R"), A=SIMP(statut="f", typ="R")),
)
