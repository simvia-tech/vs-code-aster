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

# person_in_charge: mickael.abbas at edf.fr

from ..Commons import *
from ..Language.DataStructure import *
from ..Language.Syntax import *

AFFE_MATERIAU = MACRO(
    nom="AFFE_MATERIAU",
    op=OPS("code_aster.MacroCommands.affe_materiau_ops.affe_materiau_ops"),
    sd_prod=cham_mater,
    fr=tr("Affecter des matériaux à des zones géométriques d'un maillage"),
    reentrant="n",
    regles=(AU_MOINS_UN("MAILLAGE", "MODELE"),),
    MAILLAGE=SIMP(statut="f", typ=(maillage_sdaster, maillage_p)),
    MODELE=SIMP(statut="f", typ=modele_sdaster),
    #  affectation du nom du matériau (par zone):
    #  ----------------------------------------------
    AFFE=FACT(
        statut="o",
        max="**",
        regles=(UN_PARMI("TOUT", "GROUP_MA"),),
        TOUT=SIMP(statut="f", typ="TXM", into=("OUI",)),
        GROUP_MA=SIMP(statut="f", typ=grma, validators=NoRepeat(), max="**"),
        MATER=SIMP(statut="o", typ=mater_sdaster, max=30),
    ),
    #  affectation de comportement (multifibres pour l'instant):
    #  ----------------------------------------------
    AFFE_COMPOR=FACT(
        statut="f",
        max="**",
        regles=(UN_PARMI("TOUT", "GROUP_MA"),),
        TOUT=SIMP(statut="f", typ="TXM", into=("OUI",)),
        GROUP_MA=SIMP(statut="f", typ=grma, validators=NoRepeat(), max="**"),
        COMPOR=SIMP(statut="o", typ=compor_sdaster, max=1),
    ),
    #  affectation des variables de commande :
    #  --------------------------------------------------
    AFFE_VARC=C_AFFE_VARC(),
    INFO=SIMP(statut="f", typ="I", defaut=1, into=(1, 2)),
    translation={
        "AFFE_MATERIAU": "Assign a material",
        "AFFE": "Material assignement",
        "AFFE_COMPOR": "Behaviour assignement",
        "AFFE_VARC": "External state variable assignement",
        "NOM_VARC": "External state variable",
        "NOM_CHAM": "Field name",
        "TOUT": "Everywhere",
    },
)
