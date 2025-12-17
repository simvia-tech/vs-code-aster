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

# person_in_charge: alexandre-externe.martin at edf.fr

from ..Commons import *
from ..Language.DataStructure import *
from ..Language.Syntax import *

POST_ERREUR = MACRO(
    nom="POST_ERREUR",
    op=OPS("code_aster.MacroCommands.post_erreur_ops.post_erreur_ops"),
    sd_prod=table_sdaster,
    reentrant="n",
    OPTION=SIMP(statut="o", typ="TXM", into=("DEPL_RELA", "ENER_RELA", "LAGR_RELA")),
    MODELE=SIMP(statut="o", typ=modele_sdaster),
    GROUP_MA=SIMP(statut="o", typ=grma, max="**"),
    b_depl=BLOC(
        condition="""equal_to("OPTION", 'DEPL_RELA') """,
        fr="Paramètres pour l'erreur en deplacement en norme l2",
        CHAM_MATER=SIMP(statut="f", typ=cham_mater),
        CHAM_GD=SIMP(statut="o", typ=cham_no_sdaster),
        DX=SIMP(statut="f", typ=(formule), max="**"),
        DY=SIMP(statut="f", typ=(formule), max="**"),
        DZ=SIMP(statut="f", typ=(formule), max="**"),
    ),
    b_ener=BLOC(
        condition="""equal_to("OPTION", 'ENER_RELA') """,
        fr="Paramètres pour l'erreur en energie elastique",
        CHAM_MATER=SIMP(statut="o", typ=cham_mater),
        DEFORMATION=SIMP(statut="o", typ="TXM", into=("PETIT",)),
        CHAM_GD=SIMP(statut="o", typ=cham_elem),
        SIXX=SIMP(statut="f", typ=(formule), max="**"),
        SIYY=SIMP(statut="f", typ=(formule), max="**"),
        SIZZ=SIMP(statut="f", typ=(formule), max="**"),
        SIXY=SIMP(statut="f", typ=(formule), max="**"),
        SIXZ=SIMP(statut="f", typ=(formule), max="**"),
        SIYZ=SIMP(statut="f", typ=(formule), max="**"),
    ),
    b_lag=BLOC(
        condition="""equal_to("OPTION", 'LAGR_RELA') """,
        fr="Paramètres pour l'erreur en pression en norme l2",
        CHAM_GD=SIMP(statut="o", typ=cham_no_sdaster),
        LAGS_C=SIMP(statut="f", typ=(formule), max="**"),
    ),
)
