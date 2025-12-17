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

# person_in_charge: nicolas.sellenet at edf.fr

from ..Commons import *
from ..Language.DataStructure import *
from ..Language.Syntax import *

CREA_LIB_MFRONT = MACRO(
    nom="CREA_LIB_MFRONT",
    op=OPS("code_aster.MacroCommands.crea_lib_mfront_ops.crea_lib_mfront_ops"),
    reentrant="n",
    sd_prod=compor_mgis,
    fr=tr(
        "Compiler une loi de comportement MFront ou charger un comportement "
        "depuis une bibliothèque existante"
    ),
    regles=AU_MOINS_UN("UNITE_MFRONT", "UNITE_LIBRAIRIE"),
    NOM_COMPOR=SIMP(statut="o", typ="TXM", fr=tr("Nom du comportement dans la bibliothèque")),
    UNITE_MFRONT=SIMP(statut="f", typ=UnitType(), inout="in"),
    UNITE_LIBRAIRIE=SIMP(statut="f", typ=UnitType(), inout="out"),
    DEBUG=SIMP(statut="f", typ="TXM", defaut="NON", into=("OUI", "NON")),
)
