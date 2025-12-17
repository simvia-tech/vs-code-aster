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

# person_in_charge: mathieu.courtois at edf.fr

from ..Commons import *
from ..Language.DataStructure import *
from ..Language.Syntax import *

DEFI_LIST_REEL = OPER(
    nom="DEFI_LIST_REEL",
    op=24,
    sd_prod=listr8_sdaster,
    fr=tr("Définir une liste de réels strictement croissante"),
    reentrant="n",
    regles=(
        UN_PARMI("VALE", "DEBUT"),
        EXCLUS("VALE", "INTERVALLE"),
        ENSEMBLE("DEBUT", "INTERVALLE"),
    ),
    VALE=SIMP(statut="f", typ="R", max="**"),
    DEBUT=SIMP(statut="f", typ="R"),
    INTERVALLE=FACT(
        statut="f",
        max="**",
        regles=(UN_PARMI("NOMBRE", "PAS"),),
        JUSQU_A=SIMP(statut="o", typ="R"),
        NOMBRE=SIMP(statut="f", typ="I"),
        PAS=SIMP(statut="f", typ="R"),
    ),
    INFO=SIMP(statut="f", typ="I", defaut=1, into=(1, 2)),
    TITRE=SIMP(statut="f", typ="TXM"),
)
