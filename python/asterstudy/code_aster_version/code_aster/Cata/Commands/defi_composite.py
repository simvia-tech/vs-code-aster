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

# person_in_charge: ayaovi-dzifa.kudawoo at edf.fr

from ..Commons import *
from ..Language.DataStructure import *
from ..Language.Syntax import *

DEFI_COMPOSITE = OPER(
    nom="DEFI_COMPOSITE",
    op=56,
    sd_prod=mater_sdaster,
    reentrant="n",
    fr=tr(
        "Déterminer les caractéristiques matériaux homogénéisées d'une coque multicouche à partir"
        " des caractéristiques de chaque couche"
    ),
    COUCHE=FACT(
        statut="o",
        max="**",
        EPAIS=SIMP(statut="o", typ="R", val_min=0.0e0),
        MATER=SIMP(statut="o", typ=(mater_sdaster)),
        ORIENTATION=SIMP(statut="f", typ="R", defaut=0.0e0, val_min=-90.0e0, val_max=90.0e0),
    ),
    IMPRESSION=FACT(statut="f", UNITE=SIMP(statut="f", typ=UnitType(), defaut=8, inout="out")),
)
