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

# person_in_charge: j-pierre.lefebvre at edf.fr

from ..Commons import *
from ..Language.DataStructure import *
from ..Language.Syntax import *

IMPR_CO = PROC(
    nom="IMPR_CO",
    op=17,
    fr=tr(
        "Imprimer tous les objets JEVEUX qui constituent un concept utilisateur existant (pour les développeurs)"
    ),
    regles=(UN_PARMI("CONCEPT", "CHAINE", "TOUT"),),
    UNITE=SIMP(statut="f", typ=UnitType(), defaut=8, inout="out"),
    NIVEAU=SIMP(statut="f", typ="I", defaut=2, into=(-1, 0, 1, 2)),
    ATTRIBUT=SIMP(statut="f", typ="TXM", defaut="NON", into=("NON", "OUI")),
    CONTENU=SIMP(statut="f", typ="TXM", defaut="OUI", into=("NON", "OUI")),
    BASE=SIMP(statut="f", typ="TXM", defaut="G", into=(" ", "G", "V", "L")),
    CONCEPT=FACT(
        statut="f", max="**", NOM=SIMP(statut="o", typ=assd, validators=NoRepeat(), max="**")
    ),
    CHAINE=SIMP(statut="f", typ="TXM"),
    POSITION=SIMP(statut="f", typ="I", defaut=1),
    TOUT=SIMP(statut="f", typ="TXM", into=("OUI",)),
    b_permut=BLOC(
        condition="""equal_to("NIVEAU", -1) """,
        PERMUTATION=SIMP(statut="f", typ="TXM", defaut="OUI", into=("NON", "OUI")),
    ),
)
