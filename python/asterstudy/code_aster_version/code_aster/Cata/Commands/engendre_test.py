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

# person_in_charge: jacques.pellet at edf.fr

from ..Commons import *
from ..Language.DataStructure import *
from ..Language.Syntax import *

ENGENDRE_TEST = PROC(
    nom="ENGENDRE_TEST",
    op=178,
    fr=tr("Engendre des tests pour la non régression du code (pour développeurs)"),
    UNITE=SIMP(statut="f", typ=UnitType(), defaut=8, inout="out"),
    FORMAT=SIMP(statut="f", typ="TXM", into=("ASTER", "OBJET"), defaut="ASTER"),
    FORMAT_R=SIMP(statut="f", typ="TXM", defaut="1PE20.13"),
    PREC_R=SIMP(statut="f", typ="TXM", defaut="1.E-10"),
    # ============================================================================
    b_aster=BLOC(
        condition="""equal_to("FORMAT", 'ASTER')""",
        CO=SIMP(
            statut="o",
            typ=(cham_gd_sdaster, resultat_sdaster, table_sdaster),
            validators=NoRepeat(),
            max="**",
        ),
        TYPE_TEST=SIMP(
            statut="f", typ="TXM", defaut="SOMM_ABS", into=("SOMME", "SOMM_ABS", "MAX", "MIN")
        ),
    ),
    # ============================================================================
    b_objet=BLOC(
        condition="""equal_to("FORMAT", 'OBJET')""",
        regles=(UN_PARMI("TOUT", "CO"),),
        TOUT=SIMP(statut="f", typ="TXM", into=("OUI",)),
        CO=SIMP(statut="f", typ=assd, validators=NoRepeat(), max="**"),
        TYPE_TEST=SIMP(statut="f", typ="TXM", defaut="SOMME", into=("SOMME",)),
    ),
)
