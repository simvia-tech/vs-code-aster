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

DEBUG = PROC(
    nom="DEBUG",
    op=137,
    fr=tr("Permettre de changer entre 2 commandes quelques variables globales de debug"),
    SDVERI=SIMP(
        fr=tr("vérifie la conformité des SD produites par les commandes"),
        statut="f",
        typ="TXM",
        into=("OUI", "NON"),
    ),
    JXVERI=SIMP(
        fr=tr("vérifie l intégrité de la segmentation mémoire"),
        statut="f",
        typ="TXM",
        into=("OUI", "NON"),
    ),
    JEVEUX=SIMP(
        fr=tr("force les déchargement sur disque"), statut="f", typ="TXM", into=("OUI", "NON")
    ),
    IMPR_MACRO=SIMP(
        fr=tr("affichage des sous-commandes produites par les macros dans le fichier mess"),
        statut="f",
        typ="TXM",
        into=("OUI", "NON"),
    ),
)
