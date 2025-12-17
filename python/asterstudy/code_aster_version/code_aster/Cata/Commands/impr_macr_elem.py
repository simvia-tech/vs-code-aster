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

# person_in_charge: mathieu.corus at edf.fr

from ..Commons import *
from ..Language.DataStructure import *
from ..Language.Syntax import *

IMPR_MACR_ELEM = PROC(
    nom="IMPR_MACR_ELEM",
    op=160,
    fr=tr("Impression d'une structure de données MACR_ELEM_DYNA au format IDEAS MISS3D"),
    MACR_ELEM_DYNA=SIMP(statut="o", typ=macr_elem_dyna),
    FORMAT=SIMP(statut="f", typ="TXM", defaut="IDEAS", into=("MISS_3D", "IDEAS")),
    b_ideas=BLOC(
        condition="""equal_to("FORMAT", 'IDEAS')""",
        UNITE=SIMP(statut="f", typ=UnitType(), defaut=30, inout="out"),
        VERSION=SIMP(statut="f", typ="I", defaut=5, into=(5,)),
    ),
    b_miss_3d=BLOC(
        condition="""equal_to("FORMAT", 'MISS_3D')""",
        regles=(EXCLUS("AMOR_REDUIT", "LIST_AMOR"),),
        UNITE=SIMP(statut="f", typ=UnitType(), defaut=26, inout="out"),
        SOUS_TITRE=SIMP(statut="f", typ="TXM"),
        AMOR_REDUIT=SIMP(statut="f", typ="R", max="**"),
        LIST_AMOR=SIMP(statut="f", typ=listr8_sdaster),
        GROUP_MA_INTERF=SIMP(statut="o", typ=grma, max="**"),
        GROUP_MA_FLU_STR=SIMP(statut="f", typ=grma, max="**"),
        GROUP_MA_FLU_SOL=SIMP(statut="f", typ=grma, max="**"),
        GROUP_MA_SOL_SOL=SIMP(statut="f", typ=grma, max="**"),
        GROUP_MA_CONTROL=SIMP(statut="f", typ=grma, max="**"),
        FORMAT_R=SIMP(statut="f", typ="TXM", defaut="1PE12.5", into=("1PE12.5", "1PE16.9")),
        IMPR_MODE_MECA=SIMP(statut="f", typ="TXM", defaut="OUI", into=("OUI", "NON")),
        IMPR_MODE_STAT=SIMP(statut="f", typ="TXM", defaut="OUI", into=("OUI", "NON")),
    ),
)
