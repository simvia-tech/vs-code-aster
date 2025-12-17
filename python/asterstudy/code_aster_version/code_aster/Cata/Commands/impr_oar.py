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

from ..Commons import *
from ..Language.DataStructure import *
from ..Language.Syntax import *

"""

Impression de tables code_aster au format OAR.
On imprime au choix une table de résultats sous chargement mécanique ou sous chargement thermique.

"""

IMPR_OAR = MACRO(
    nom="IMPR_OAR",
    op=OPS("code_aster.MacroCommands.impr_oar_ops.impr_oar_ops"),
    sd_prod=None,
    fr=tr("Impression au format OAR"),
    regles=(UN_PARMI("TABL_MECA", "TABL_THER")),
    TABL_MECA=FACT(
        statut="f",
        max="**",
        PRESSION=SIMP(statut="f", typ=table_sdaster),
        FLEXION_P=SIMP(statut="f", typ=table_sdaster),
        FLEXION_HP=SIMP(statut="f", typ=table_sdaster),
        TORSION=SIMP(statut="f", typ=table_sdaster),
    ),
    TABL_THER=FACT(
        statut="f",
        max="**",
        regles=(AU_MOINS_UN("TEMP", "CONTRAINTE")),
        TEMP=SIMP(statut="f", typ=table_sdaster),
        CONTRAINTE=SIMP(statut="f", typ=table_sdaster),
    ),
    UNITE=SIMP(
        statut="o",
        typ=UnitType(),
        inout="out",
        fr=tr("Unité logique définissant le fichier (fort.N) dans lequel on écrit"),
    ),
    TITRE=SIMP(statut="f", typ="TXM"),
    TYPE_UNIT=SIMP(statut="f", typ="TXM", defaut="SI"),
)
