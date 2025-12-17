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

# person_in_charge: kyrylo.kazymyrenko at edf.fr
# ----------------------------------------------------------------------
#  POST_CZM_FISS :
#  ---------------
#  OPTION = 'LONGUEUR'
#    - CALCUL DE LA LONGUEUR DES FISSURES COHESIVES 2D
#    - PRODUIT UNE TABLE
#  OPTION = 'TRIAXIALITE'
#    - CALCUL DE LA TRIAXIALITE DANS LES ELEMENTS MASSIFS CONNECTES A
#      L'INTERFACE COHESIVE
#    - PRODUIT UNE CARTE
# ----------------------------------------------------------------------

from ..Commons import *
from ..Language.DataStructure import *
from ..Language.Syntax import *


def post_czm_fiss_prod(self, OPTION, **args):
    if args.get("__all__"):
        return (table_sdaster, carte_sdaster)
    if OPTION == "LONGUEUR":
        return table_sdaster
    if OPTION == "TRIAXIALITE":
        return carte_sdaster
    raise AsException("type de concept resultat non prevu")


POST_CZM_FISS = MACRO(
    nom="POST_CZM_FISS",
    op=OPS("code_aster.MacroCommands.post_czm_fiss_ops.post_czm_fiss_ops"),
    sd_prod=post_czm_fiss_prod,
    reentrant="n",
    fr=tr("Post-Traiement scpécifiques aux modèles CZM"),
    OPTION=SIMP(statut="o", typ="TXM", max=1, into=("LONGUEUR", "TRIAXIALITE")),
    RESULTAT=SIMP(statut="o", typ=evol_noli, max=1),
    b_longueur=BLOC(
        condition="""equal_to("OPTION", 'LONGUEUR') """,
        GROUP_MA=SIMP(statut="o", typ=grma, validators=NoRepeat(), max="**"),
        POINT_ORIG=SIMP(statut="o", typ="R", min=2, max=2),
        VECT_TANG=SIMP(statut="o", typ="R", min=2, max=2),
    ),
)
