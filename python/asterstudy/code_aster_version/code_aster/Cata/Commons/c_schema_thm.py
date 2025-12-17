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
# person_in_charge: sylvie.granet at edf.fr

from ..Language.DataStructure import *
from ..Language.Syntax import *


def C_SCHEMA_THM():
    return FACT(
        statut="f",
        max=1,
        PARM_THETA=SIMP(statut="f", typ="R", val_min=0.0, val_max=1.0, defaut=1.0),
        PARM_ALPHA=SIMP(statut="f", typ="R", defaut=1.0),
    )
