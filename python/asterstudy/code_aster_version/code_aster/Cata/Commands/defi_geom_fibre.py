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

from ..Commons import *
from ..Language.DataStructure import *
from ..Language.Syntax import *

DEFI_GEOM_FIBRE = OPER(
    nom="DEFI_GEOM_FIBRE",
    op=119,
    sd_prod=gfibre_sdaster,
    fr=tr("Definition des groupes de fibres pour les elements multifibres"),
    reentrant="n",
    regles=(AU_MOINS_UN("SECTION", "FIBRE"),),
    INFO=SIMP(statut="f", typ="I", defaut=1, into=(1, 2)),
    # ============================================================================
    SECTION=FACT(
        statut="f",
        max="**",
        regles=(
            AU_MOINS_UN("TOUT_SECT", "GROUP_MA_SECT"),
            PRESENT_ABSENT("TOUT_SECT", "GROUP_MA_SECT"),
        ),
        GROUP_FIBRE=SIMP(statut="o", typ="TXM", min=1, max=1),
        TOUT_SECT=SIMP(statut="f", typ="TXM", into=("OUI",)),
        GROUP_MA_SECT=SIMP(statut="f", typ=grma, validators=NoRepeat(), max="**"),
        MAILLAGE_SECT=SIMP(statut="o", typ=maillage_sdaster),
        COOR_AXE_POUTRE=SIMP(statut="o", typ="R", min=2, max=2),
        ANGLE=SIMP(statut="f", typ="R", max=1, defaut=0.0),
    ),
    # ============================================================================
    FIBRE=FACT(
        statut="f",
        max="**",
        GROUP_FIBRE=SIMP(statut="o", typ="TXM", min=1, max=1),
        CARA=SIMP(statut="f", typ="TXM", defaut="SURFACE", into=("SURFACE", "DIAMETRE")),
        VALE=SIMP(statut="o", typ="R", max="**"),
        COOR_AXE_POUTRE=SIMP(statut="o", typ="R", min=2, max=2),
        ANGLE=SIMP(statut="f", typ="R", max=1, defaut=0.0),
    ),
    # ============================================================================
    ASSEMBLAGE_FIBRE=FACT(
        statut="f",
        max="**",
        GROUP_ASSE_FIBRE=SIMP(statut="o", typ="TXM", min=1, max=1),
        GROUP_FIBRE=SIMP(statut="o", typ="TXM", min=1, max="**"),
        COOR_GROUP_FIBRE=SIMP(statut="o", typ="R", min=2, max="**"),
        GX_GROUP_FIBRE=SIMP(statut="o", typ="R", min=1, max="**"),
    ),
)
