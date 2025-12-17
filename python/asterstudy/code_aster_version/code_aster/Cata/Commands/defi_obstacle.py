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

# person_in_charge: marc.kham at edf.fr

from ..Commons import *
from ..Language.DataStructure import *
from ..Language.Syntax import *

DEFI_OBSTACLE = OPER(
    nom="DEFI_OBSTACLE",
    op=73,
    sd_prod=table_fonction,
    fr=tr("Définition d'un obstacle plan perpendiculaire à une structure filaire"),
    reentrant="n",
    TYPE=SIMP(
        statut="f",
        typ="TXM",
        defaut="CERCLE",
        into=(
            "CERCLE",
            "PLAN_Y",
            "PLAN_Z",
            "DISCRET",
            "BI_CERCLE",
            "BI_PLAN_Y",
            "BI_PLAN_Z",
            "BI_CERC_INT",
        ),
    ),
    VALE=SIMP(statut="f", typ="R", max="**"),
    VERIF=SIMP(statut="f", typ="TXM", defaut="FERME"),
)
