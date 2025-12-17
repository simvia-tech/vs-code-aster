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

# person_in_charge: ayaovi-dzifa.kudawoo at edf.fr

from ..Commons import *
from ..Language.DataStructure import *
from ..Language.Syntax import *

POST_COQUE = MACRO(
    nom="POST_COQUE",
    op=OPS("code_aster.MacroCommands.post_coque_ops.post_coque_ops"),
    sd_prod=table_sdaster,
    reentrant="n",
    fr=tr("Calcul des efforts et déformations en un point et une cote " "quelconque de la coque"),
    regles=(EXCLUS("INST", "NUME_ORDRE"),),
    # SD résultat et champ à posttraiter :
    RESULTAT=SIMP(statut="o", typ=resultat_sdaster, fr=tr("RESULTAT à posttraiter")),
    CHAM=SIMP(statut="o", typ="TXM", into=("EFFORT", "DEFORMATION")),
    NUME_ORDRE=SIMP(statut="f", typ="I"),
    INST=SIMP(statut="f", typ="R"),
    # points de post-traitement :
    COOR_POINT=FACT(
        statut="o",
        max="**",
        fr=tr("coordonnées et position dans l'épaisseur"),
        COOR=SIMP(statut="o", typ="R", min=3, max=4),
    ),
)
