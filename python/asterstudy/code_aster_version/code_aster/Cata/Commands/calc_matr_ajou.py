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

# person_in_charge: nicolas.greffet at edf.fr

from ..Commons import *
from ..Language.DataStructure import *
from ..Language.Syntax import *

CALC_MATR_AJOU = OPER(
    nom="CALC_MATR_AJOU",
    op=152,
    sd_prod=matr_asse_gene_r,
    fr=tr("Calcul des matrices de masse, d'amortissement ou de rigidité ajoutés"),
    reentrant="n",
    regles=(
        EXCLUS("MODE_MECA", "CHAM_NO", "MODELE_GENE"),
        PRESENT_ABSENT("NUME_DDL_GENE", "CHAM_NO"),
        PRESENT_PRESENT("MODE_MECA", "NUME_DDL_GENE"),
        PRESENT_PRESENT("MODELE_GENE", "NUME_DDL_GENE"),
    ),
    MODELE_FLUIDE=SIMP(statut="o", typ=modele_sdaster),
    MODELE_INTERFACE=SIMP(statut="o", typ=modele_sdaster),
    CHAM_MATER=SIMP(statut="o", typ=cham_mater),
    CHARGE=SIMP(statut="o", typ=char_ther, max=1),
    MODE_MECA=SIMP(statut="f", typ=mode_meca),
    CHAM_NO=SIMP(statut="f", typ=cham_no_sdaster),
    MODELE_GENE=SIMP(statut="f", typ=modele_gene),
    NUME_DDL_GENE=SIMP(statut="f", typ=nume_ddl_gene),
    DIST_REFE=SIMP(statut="f", typ="R", defaut=1.0e-2),
    AVEC_MODE_STAT=SIMP(statut="f", typ="TXM", defaut="OUI", into=("OUI", "NON")),
    NUME_MODE_MECA=SIMP(statut="f", typ="I", validators=NoRepeat(), max="**"),
    OPTION=SIMP(statut="o", typ="TXM", into=("MASS_AJOU", "AMOR_AJOU", "RIGI_AJOU")),
    POTENTIEL=SIMP(statut="f", typ=evol_ther),
    NOEUD_DOUBLE=SIMP(statut="f", typ="TXM", defaut="NON", into=("OUI", "NON")),
    INFO=SIMP(statut="f", typ="I", defaut=1, into=(1, 2)),
    # -------------------------------------------------------------------
    #        Catalogue commun SOLVEUR
    SOLVEUR=C_SOLVEUR("CALC_MATR_AJOU"),
    # -------------------------------------------------------------------
)
