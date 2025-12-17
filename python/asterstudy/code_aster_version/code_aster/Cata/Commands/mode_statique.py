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

# person_in_charge: georges-cc.devesa at edf.fr

from ..Commons import *
from ..Language.DataStructure import *
from ..Language.Syntax import *

MODE_STATIQUE = OPER(
    nom="MODE_STATIQUE",
    op=93,
    sd_prod=mode_meca,
    fr=tr(
        "Calcul de déformées statiques pour un déplacement, une force ou une accélération unitaire imposé"
    ),
    reentrant="n",
    regles=(
        UN_PARMI("MODE_STAT", "FORCE_NODALE", "PSEUDO_MODE", "MODE_INTERF"),
        PRESENT_PRESENT("MODE_INTERF", "MATR_MASS"),
        PRESENT_PRESENT("PSEUDO_MODE", "MATR_MASS"),
    ),
    MATR_RIGI=SIMP(statut="o", typ=matr_asse_depl_r),
    MATR_MASS=SIMP(statut="f", typ=matr_asse_depl_r),
    MODE_STAT=FACT(
        statut="f",
        max="**",
        regles=(
            UN_PARMI("TOUT", "NOEUD", "GROUP_NO"),
            UN_PARMI("TOUT_CMP", "AVEC_CMP", "SANS_CMP"),
        ),
        TOUT=SIMP(statut="f", typ="TXM", into=("OUI",)),
        NOEUD=SIMP(statut="c", typ=no, max="**"),
        GROUP_NO=SIMP(statut="f", typ=grno, max="**"),
        TOUT_CMP=SIMP(statut="f", typ="TXM", into=("OUI",)),
        AVEC_CMP=SIMP(statut="f", typ="TXM", max="**"),
        SANS_CMP=SIMP(statut="f", typ="TXM", max="**"),
    ),
    FORCE_NODALE=FACT(
        statut="f",
        max="**",
        regles=(
            UN_PARMI("TOUT", "NOEUD", "GROUP_NO"),
            UN_PARMI("TOUT_CMP", "AVEC_CMP", "SANS_CMP"),
        ),
        TOUT=SIMP(statut="f", typ="TXM", into=("OUI",)),
        NOEUD=SIMP(statut="c", typ=no, max="**"),
        GROUP_NO=SIMP(statut="f", typ=grno, max="**"),
        TOUT_CMP=SIMP(statut="f", typ="TXM", into=("OUI",)),
        AVEC_CMP=SIMP(statut="f", typ="TXM", max="**"),
        SANS_CMP=SIMP(statut="f", typ="TXM", max="**"),
    ),
    PSEUDO_MODE=FACT(
        statut="f",
        max="**",
        regles=(UN_PARMI("AXE", "DIRECTION", "TOUT", "GROUP_NO"),),
        AXE=SIMP(statut="f", typ="TXM", into=("X", "Y", "Z"), max=3),
        DIRECTION=SIMP(statut="f", typ="R", min=3, max=3),
        TOUT=SIMP(statut="f", typ="TXM", into=("OUI",)),
        GROUP_NO=SIMP(statut="f", typ=grno, max="**"),
        b_dir=BLOC(condition="""exists("DIRECTION")""", NOM_DIR=SIMP(statut="o", typ="TXM")),
        b_cmp=BLOC(
            condition="""exists("TOUT") or exists("NOEUD") or exists("GROUP_NO")""",
            regles=(UN_PARMI("TOUT_CMP", "AVEC_CMP", "SANS_CMP"),),
            TOUT_CMP=SIMP(statut="f", typ="TXM", into=("OUI",)),
            AVEC_CMP=SIMP(statut="f", typ="TXM", max="**"),
            SANS_CMP=SIMP(statut="f", typ="TXM", max="**"),
        ),
    ),
    MODE_INTERF=FACT(
        statut="f",
        max=1,
        regles=(UN_PARMI("TOUT", "GROUP_NO"), UN_PARMI("TOUT_CMP", "AVEC_CMP", "SANS_CMP")),
        TOUT=SIMP(statut="f", typ="TXM", into=("OUI",)),
        GROUP_NO=SIMP(statut="f", typ=grno, max="**"),
        TOUT_CMP=SIMP(statut="f", typ="TXM", into=("OUI",)),
        AVEC_CMP=SIMP(statut="f", typ="TXM", max="**"),
        SANS_CMP=SIMP(statut="f", typ="TXM", max="**"),
        NB_MODE=SIMP(statut="f", typ="I", defaut=1),
        SHIFT=SIMP(statut="f", typ="R", defaut=1.0),
    ),
    # -------------------------------------------------------------------
    #        Catalogue commun SOLVEUR
    SOLVEUR=C_SOLVEUR("MODE_STATIQUE"),
    # -------------------------------------------------------------------
    TITRE=SIMP(statut="f", typ="TXM"),
    INFO=SIMP(statut="f", typ="I", defaut=1, into=(1, 2)),
)
