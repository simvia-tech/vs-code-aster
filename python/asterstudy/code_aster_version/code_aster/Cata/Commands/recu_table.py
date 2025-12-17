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

RECU_TABLE = OPER(
    nom="RECU_TABLE",
    op=174,
    sd_prod=table_sdaster,
    fr=tr(
        "Récupérer dans une table les valeurs d'un paramètre d'une SD Résultat ou d'extraire une table contenue"
        " dans une autre SD pour celles qui le permettent"
    ),
    CO=SIMP(statut="o", typ=assd),
    regles=(UN_PARMI("NOM_TABLE", "NOM_PARA", "TOUT_PARA")),
    NOM_TABLE=SIMP(statut="f", typ="TXM"),
    NOM_PARA=SIMP(statut="f", typ="TXM", max="**"),
    TOUT_PARA=SIMP(statut="f", typ="TXM", into=("OUI",)),
    TITRE=SIMP(statut="f", typ="TXM"),
)
