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

# person_in_charge: samuel.jules at edf.fr

from ..Commons import *
from ..Language.DataStructure import *
from ..Language.Syntax import *

POST_FM = MACRO(
    nom="POST_FM",
    op=OPS("code_aster.MacroCommands.post_fm_ops.post_fm_ops"),
    sd_prod=table_sdaster,
    fr=tr("Opérateur de calcul des facteurs de marge"),
    reentrant="n",
    RESULTAT=SIMP(statut="o", min=1, max=1, typ=(evol_elas, evol_noli)),
    TABLE_G=SIMP(statut="o", min=1, max=1, typ=(table_sdaster, table_container)),
    GROUP_NO=SIMP(statut="o", typ=grno, validators=NoRepeat(), min=1, max=1),
)
