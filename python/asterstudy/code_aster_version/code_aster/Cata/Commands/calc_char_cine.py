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

# person_in_charge: jacques.pellet at edf.fr

from ..Commons import *
from ..Language.DataStructure import *
from ..Language.Syntax import *

CALC_CHAR_CINE = MACRO(
    nom="CALC_CHAR_CINE",
    op=OPS("code_aster.MacroCommands.calc_char_cine_ops.calc_char_cine_ops"),
    sd_prod=cham_no_sdaster,
    fr=tr(
        "Calcul des seconds membres associés à des charges cinématiques (conditions aux limites non dualisées)"
    ),
    reentrant="n",
    NUME_DDL=SIMP(statut="o", typ=nume_ddl_sdaster),
    CHAR_CINE=SIMP(
        statut="o",
        typ=(char_cine_meca, char_cine_ther, char_cine_acou),
        validators=NoRepeat(),
        max="**",
    ),
    INST=SIMP(statut="f", typ="R", defaut=0.0e0),
    INFO=SIMP(statut="f", typ="I", defaut=1, into=(1, 2)),
)
