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

# person_in_charge: david.haboussa at edf.fr

from ..Commons import *
from ..Language.DataStructure import *
from ..Language.Syntax import *

RAFF_GP = MACRO(
    nom="RAFF_GP",
    op=OPS("code_aster.MacroCommands.raff_gp_ops.raff_gp_ops"),
    sd_prod=maillage_sdaster,
    reentrant="n",
    fr=tr("Preparation du maillage pour calcul du Gp en 2D"),
    MAILLAGE_N=SIMP(statut="o", typ=maillage_sdaster, fr=tr("Maillage avant adaptation")),
    TRANCHE_2D=FACT(
        statut="o",
        max=1,
        CENTRE=SIMP(statut="o", typ="R", max=2),
        RAYON=SIMP(statut="o", typ="R", max=1),
        ANGLE=SIMP(statut="o", typ="R", max=1),
        TAILLE=SIMP(statut="o", typ="R", max=1),
        NB_ZONE=SIMP(statut="o", typ="I"),
    ),
    NB_RAFF=SIMP(statut="f", typ="I", defaut=4),
)
