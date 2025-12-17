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

LIRE_TABLE = MACRO(
    nom="LIRE_TABLE",
    op=OPS("code_aster.MacroCommands.lire_table_ops.lire_table_ops"),
    sd_prod=table_sdaster,
    fr=tr("Lecture d'un fichier contenant une table"),
    UNITE=SIMP(statut="o", typ=UnitType(), inout="in"),
    FORMAT=SIMP(statut="f", typ="TXM", into=("ASTER", "LIBRE", "TABLEAU"), defaut="TABLEAU"),
    NUME_TABLE=SIMP(statut="f", typ="I", defaut=1),
    SEPARATEUR=SIMP(statut="f", typ="TXM", defaut=" "),
    RENOMME_PARA=SIMP(statut="f", typ="TXM", into=("UNIQUE",)),
    TITRE=SIMP(statut="f", typ="TXM"),
    INFO=SIMP(statut="f", typ="I", into=(1, 2)),
)
