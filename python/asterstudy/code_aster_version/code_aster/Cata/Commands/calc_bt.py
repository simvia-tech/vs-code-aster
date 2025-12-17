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

from ..Commons import *
from ..Language.DataStructure import *
from ..Language.Syntax import *


def calc_bt_prod(self, RESU_BT, **args):
    if args.get("__all__"):
        return ([table_sdaster], [evol_elas])
    # On definit ici les concepts produits
    self.type_sdprod(RESU_BT, evol_elas)
    # concept retourne
    return table_sdaster


# Formalisation de la macro commande CALC_CARTEDEV
CALC_BT = MACRO(
    nom="CALC_BT",
    op=OPS("code_aster.MacroCommands.calc_bt_ops.calc_bt_ops"),
    fr=tr("Modéle Bielles-Tirants à partir d'un modéle 2D"),
    sd_prod=calc_bt_prod,
    reentrant="n",
    #      CONCEPT SORTANT
    #      ********************************************
    RESU_BT=SIMP(statut="f", typ=CO),
    #      MODEL INITIAL
    #      ********************************************
    RESULTAT=SIMP(statut="o", typ=(evol_elas, evol_noli)),
    INST=SIMP(statut="f", typ="R", defaut=0.0),
    DDL_IMPO=FACT(
        statut="o",
        max="**",
        GROUP_NO=SIMP(statut="o", typ="TXM", fr=tr("Groupe de noeuds associé aux blocages")),
        DY=SIMP(statut="f", typ="R"),
        DX=SIMP(statut="f", typ="R"),
    ),
    FORCE_NODALE=FACT(
        statut="o",
        max="**",
        GROUP_NO=SIMP(statut="o", typ="TXM", fr=tr("Groupe de noeuds associé aux forces imposees")),
        FY=SIMP(statut="f", typ="R", defaut=0.0),
        FX=SIMP(statut="f", typ="R", defaut=0.0),
    ),
    BETON=SIMP(statut="o", typ=mater_sdaster),
    ACIER=SIMP(statut="o", typ=mater_sdaster),
    GROUP_MA_EXT=SIMP(statut="o", typ="TXM", fr=tr("Groupe de mailles definisant le contour")),
    GROUP_MA_INT=SIMP(
        statut="f", typ="TXM", max="**", fr=tr("Groupe de mailles definisant le contour")
    ),
    SCHEMA=SIMP(
        statut="f",
        typ="TXM",
        defaut="SECTION",
        into=("SECTION", "TOPO"),
        max=1,
        fr=tr("Schema d'optimisation"),
    ),
    SIGMA_C=SIMP(statut="o", typ="R", val_min=0),
    SIGMA_Y=SIMP(statut="o", typ="R", val_min=0),
    PAS_X=SIMP(
        statut="o",
        typ="R",
        val_min=0,
        max=1,
        fr=tr("Paramètre de l'interpolation des pics de contraint. Pas selon la direction X."),
    ),
    PAS_Y=SIMP(
        statut="o",
        typ="R",
        val_min=0,
        max=1,
        fr=tr("Paramètre de l'interpolation des pics de contraint. Pas selon la direction Y."),
    ),
    TOLE_BASE=SIMP(
        statut="f",
        typ="R",
        defaut=0.01,
        val_min=0,
        max=1,
        fr=tr("Distance tolerée pour l'interpolation de pics de contrainte."),
    ),
    TOLE_BT=SIMP(
        statut="f",
        typ="R",
        val_min=0,
        max=1,
        fr=tr("Distance tolerée pour la fusion des noeuds du treillis."),
    ),
    NMAX_ITER=SIMP(
        statut="f", typ="I", defaut=150, val_min=1, max=1, fr=tr("Nombre maximum d'iterations")
    ),
    RESI_RELA_TOPO=SIMP(
        statut="f",
        typ="R",
        defaut=1e-6,
        val_min=0,
        max=1,
        fr=tr("Précision de convergence de la procédure d'optimisation de section"),
    ),
    RESI_RELA_SECTION=SIMP(
        statut="f",
        typ="R",
        defaut=1e-5,
        val_min=0,
        max=1,
        fr=tr("Précision de convergence de la procédure d'optimisation de topologique"),
    ),
    CRIT_SECTION=SIMP(
        statut="f",
        typ="R",
        defaut=0.5,
        val_min=0,
        max=1,
        fr=tr("Taux d'évolution maximale des sections"),
    ),
    CRIT_ELIM=SIMP(
        statut="f",
        typ="R",
        defaut=0.5,
        val_min=0,
        max=1,
        fr=tr("Taux maximale d'élimination  des éléments"),
    ),
    SECTION_MINI=SIMP(statut="o", typ="R", val_min=0, max=1, fr=tr("Sections minimale")),
    LONGUEUR_MAX=SIMP(statut="o", typ="R", val_min=0, fr=tr("Longueur maximale")),
    INIT_ALEA=SIMP(statut="f", typ="I", fr=tr("Germ of the random field")),
)
