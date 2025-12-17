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

# person_in_charge: harinaivo.andriambololona at edf.fr

from ..Commons import *
from ..Language.DataStructure import *
from ..Language.Syntax import *

MAC_MODES = OPER(
    nom="MAC_MODES",
    op=141,
    sd_prod=table_sdaster,
    fr=tr("Critere orthogonalite de modes propres"),
    reentrant="n",
    regles=(PRESENT_PRESENT("IERI", "MATR_ASSE"),),
    BASE_1=SIMP(statut="o", typ=(mode_meca, mode_meca_c, mode_flamb)),
    BASE_2=SIMP(statut="o", typ=(mode_meca, mode_meca_c, mode_flamb)),
    MATR_ASSE=SIMP(statut="f", typ=(matr_asse_depl_r, matr_asse_depl_c)),
    IERI=SIMP(statut="f", typ="TXM", into=("OUI",)),
    TITRE=SIMP(statut="f", typ="TXM"),
    INFO=SIMP(statut="f", typ="I", defaut=1, into=(1, 2)),
)
