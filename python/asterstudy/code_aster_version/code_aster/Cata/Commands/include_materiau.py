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

INCLUDE_MATERIAU = MACRO(
    nom="INCLUDE_MATERIAU",
    op=OPS("code_aster.MacroCommands.include_materiau_ops.include_materiau_ops"),
    sd_prod=mater_sdaster,
    fr=tr("Récupérer les caractéristiques d'un matériau dans le Catalogue Materiaux d'Aster "),
    regles=(
        UN_PARMI("NOM_AFNOR", "FICHIER"),
        ENSEMBLE("NOM_AFNOR", "TYPE_MODELE", "VARIANTE", "TYPE_VALE"),
    ),
    NOM_AFNOR=SIMP(statut="f", typ="TXM"),
    TYPE_MODELE=SIMP(statut="f", typ="TXM", into=("REF", "PAR")),
    VARIANTE=SIMP(
        statut="f",
        typ="TXM",
        into=(
            "A",
            "B",
            "C",
            "D",
            "E",
            "F",
            "G",
            "H",
            "I",
            "J",
            "K",
            "L",
            "M",
            "N",
            "O",
            "P",
            "Q",
            "R",
            "S",
            "T",
            "U",
            "V",
            "W",
            "X",
            "Y",
            "Z",
        ),
    ),
    TYPE_VALE=SIMP(statut="f", typ="TXM", into=("NOMI", "MINI", "MAXI")),
    # or
    FICHIER=SIMP(statut="f", typ="TXM", fr=tr("Nom du fichier de données à inclure")),
    EXTRACTION=FACT(
        statut="f",
        COMPOR=SIMP(statut="o", typ="TXM", max="**"),
        TEMP_EVAL=SIMP(statut="o", typ="R"),
    ),
    UNITE_LONGUEUR=SIMP(statut="f", typ="TXM", into=("M", "MM"), defaut="M"),
    PROL_DROITE=SIMP(statut="f", typ="TXM", defaut="EXCLU", into=("CONSTANT", "LINEAIRE", "EXCLU")),
    PROL_GAUCHE=SIMP(statut="f", typ="TXM", defaut="EXCLU", into=("CONSTANT", "LINEAIRE", "EXCLU")),
    INFO=SIMP(statut="f", typ="I", defaut=1, into=(1, 2)),
)
