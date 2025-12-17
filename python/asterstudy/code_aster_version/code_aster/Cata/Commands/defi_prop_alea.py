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

# person_in_charge: irmela.zentner at edf.fr

from ..Commons import *
from ..Language.DataStructure import *
from ..Language.Syntax import *

DEFI_PROP_ALEA = MACRO(
    nom="DEFI_PROP_ALEA",
    op=OPS("code_aster.MacroCommands.defi_prop_alea_ops.defi_prop_alea_ops"),
    sd_prod=formule,
    fr=tr("Construit un champ aleatoire par son expression analytique"),
    reentrant="n",
    INIT_ALEA=SIMP(statut="o", typ="I"),
    MEDIANE=SIMP(statut="o", typ="R", fr=tr("Valeur médiane de la propriété")),
    COEF_VARI=SIMP(statut="o", typ="R", fr=tr("Coefficient de variation")),
    regles=(
        AU_MOINS_UN("LONG_CORR_X", "LONG_CORR_Y", "LONG_CORR_Z"),
        EXCLUS("PRECISION", "NB_TERM"),
    ),
    LONG_CORR_X=SIMP(statut="f", typ="R", fr=tr("Longueur de corrélation en X")),
    LONG_CORR_Y=SIMP(statut="f", typ="R", fr=tr("Longueur de corrélation en Y")),
    LONG_CORR_Z=SIMP(statut="f", typ="R", fr=tr("Longueur de corrélation en Z")),
    PRECISION=SIMP(
        statut="f",
        typ="R",
        val_min=0.00001,
        val_max=1.0,
        fr=tr("Pourcentage de l'energie à retenir"),
    ),
    NB_TERM=SIMP(statut="f", typ="I", fr=tr("Nombre total de termes de KL")),
    #
    a_data_x=BLOC(
        condition="""exists('LONG_CORR_X')""",
        X_MINI=SIMP(statut="o", typ="R", fr=tr("Dimension du domaine: X_MINI")),
        X_MAXI=SIMP(statut="o", typ="R", fr=tr("Dimension du domaine: X_MAXI")),
        NB_TERM_X=SIMP(statut="o", typ="I", fr=tr("Nombre de termes de KL en X")),
    ),
    a_data_y=BLOC(
        condition="""exists('LONG_CORR_Y')""",
        Y_MINI=SIMP(statut="o", typ="R", fr=tr("Dimension du domaine: Y_MINI")),
        Y_MAXI=SIMP(statut="o", typ="R", fr=tr("Dimension du domaine: Y_MAXI")),
        NB_TERM_Y=SIMP(statut="o", typ="I", fr=tr("Nombre de termes de KL en Y")),
    ),
    a_data_z=BLOC(
        condition="""exists('LONG_CORR_Z')""",
        Z_MINI=SIMP(statut="o", typ="R", fr=tr("Dimension du domaine: Z_MINI")),
        Z_MAXI=SIMP(statut="o", typ="R", fr=tr("Dimension du domaine: Z_MAXI")),
        NB_TERM_Z=SIMP(statut="o", typ="I", fr=tr("Nombre de termes de KL en Z")),
    ),
)
