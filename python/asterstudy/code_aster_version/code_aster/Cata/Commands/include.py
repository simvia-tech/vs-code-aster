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

# person_in_charge: mathieu.courtois at edf.fr

from ..Commons import *
from ..Language.DataStructure import *
from ..Language.Syntax import *

INCLUDE = MACRO(
    nom="INCLUDE",
    op=None,
    fr=tr("Débranchement vers un fichier de commandes secondaires"),
    regles=(UN_PARMI("UNITE", "DONNEE")),
    UNITE=SIMP(statut="f", typ=UnitType(), inout="in", fr=tr("Unité logique à inclure")),
    DONNEE=SIMP(statut="f", typ="TXM", fr=tr("Nom du fichier de données à inclure")),
    ALARME=SIMP(statut="f", typ="TXM", defaut="OUI", into=("OUI", "NON")),
    INFO=SIMP(statut="f", typ="I", defaut=1, into=(0, 1, 2)),
)
