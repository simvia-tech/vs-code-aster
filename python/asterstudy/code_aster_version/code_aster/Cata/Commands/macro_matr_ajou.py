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

# person_in_charge: nicolas.greffet at edf.fr


from ..Commons import *
from ..Language.DataStructure import *
from ..Language.Syntax import *


def macro_matr_ajou_prod(
    self, MATR_AMOR_AJOU=None, MATR_MASS_AJOU=None, MATR_RIGI_AJOU=None, FORC_AJOU=None, **args
):
    if args.get("__all__"):
        return (
            [None],
            [None, matr_asse_gene_r],
            [None, matr_asse_gene_r],
            [None, matr_asse_gene_r],
            [None, vect_asse_gene],
        )

    if MATR_AMOR_AJOU is not None:
        self.type_sdprod(MATR_AMOR_AJOU, matr_asse_gene_r)
    if MATR_MASS_AJOU is not None:
        self.type_sdprod(MATR_MASS_AJOU, matr_asse_gene_r)
    if MATR_RIGI_AJOU is not None:
        self.type_sdprod(MATR_RIGI_AJOU, matr_asse_gene_r)
    if FORC_AJOU is not None:
        for m in FORC_AJOU:
            self.type_sdprod(m["VECTEUR"], vect_asse_gene)
    return None


MACRO_MATR_AJOU = MACRO(
    nom="MACRO_MATR_AJOU",
    op=OPS("code_aster.MacroCommands.macro_matr_ajou_ops.macro_matr_ajou_ops"),
    sd_prod=macro_matr_ajou_prod,
    fr=tr(
        "Calculer de facon plus condensée qu'avec CALC_MATR_AJOU des "
        "matrices de masse, d'amortissement ou de rigidité ajoutés"
    ),
    regles=(
        AU_MOINS_UN("MODE_MECA", "DEPL_IMPO", "MODELE_GENE"),
        AU_MOINS_UN("MATR_MASS_AJOU", "MATR_AMOR_AJOU", "MATR_RIGI_AJOU"),
        EXCLUS("MODE_MECA", "DEPL_IMPO", "MODELE_GENE"),
        EXCLUS("MONO_APPUI", "MODE_STAT"),
        PRESENT_ABSENT("NUME_DDL_GENE", "DEPL_IMPO"),
        PRESENT_PRESENT("MODE_MECA", "NUME_DDL_GENE"),
        PRESENT_PRESENT("MODELE_GENE", "NUME_DDL_GENE"),
    ),
    MAILLAGE=SIMP(statut="o", typ=maillage_sdaster),
    GROUP_MA_FLUIDE=SIMP(statut="o", typ=grma),
    GROUP_MA_INTERF=SIMP(statut="o", typ=grma),
    MODELISATION=SIMP(statut="o", typ="TXM", into=("PLAN", "AXIS", "3D")),
    FLUIDE=FACT(
        statut="o",
        max="**",
        RHO=SIMP(statut="o", typ="R"),
        TOUT=SIMP(statut="f", typ="TXM", into=("OUI",)),
        GROUP_MA=SIMP(statut="f", typ=grma),
    ),
    DDL_IMPO=FACT(
        statut="o",
        max="**",
        regles=(UN_PARMI("PRES_FLUIDE", "PRES_SORTIE")),
        GROUP_NO=SIMP(statut="o", typ=grno),
        PRES_FLUIDE=SIMP(statut="f", typ="R"),
        PRES_SORTIE=SIMP(statut="f", typ="R"),
    ),
    ECOULEMENT=FACT(
        statut="f",
        GROUP_MA_1=SIMP(statut="o", typ=grma),
        GROUP_MA_2=SIMP(statut="o", typ=grma),
        VNOR_1=SIMP(statut="o", typ="R"),
        VNOR_2=SIMP(statut="f", typ="R"),
        POTENTIEL=SIMP(statut="f", typ=evol_ther),
    ),
    MODE_MECA=SIMP(statut="f", typ=mode_meca),
    DEPL_IMPO=SIMP(statut="f", typ=cham_no_sdaster),
    MODELE_GENE=SIMP(statut="f", typ=modele_gene),
    NUME_DDL_GENE=SIMP(statut="f", typ=nume_ddl_gene),
    DIST_REFE=SIMP(statut="f", typ="R", defaut=1.0e-2),
    MATR_MASS_AJOU=SIMP(statut="f", typ=CO),
    MATR_RIGI_AJOU=SIMP(statut="f", typ=CO),
    MATR_AMOR_AJOU=SIMP(statut="f", typ=CO),
    MONO_APPUI=SIMP(statut="f", typ="TXM", into=("OUI",)),
    MODE_STAT=SIMP(statut="f", typ=mode_meca),
    FORC_AJOU=FACT(
        statut="f",
        max="**",
        DIRECTION=SIMP(statut="o", typ="R", max=3),
        GROUP_NO=SIMP(statut="f", typ=grno, validators=NoRepeat(), max="**"),
        VECTEUR=SIMP(statut="o", typ=CO),
    ),
    # -------------------------------------------------------------------
    #        Catalogue commun SOLVEUR
    SOLVEUR=C_SOLVEUR("MACRO_MATR_AJOU"),
    # -------------------------------------------------------------------
    INFO=SIMP(statut="f", typ="I", defaut=1, into=(1, 2)),
    NOEUD_DOUBLE=SIMP(statut="f", typ="TXM", defaut="NON", into=("OUI", "NON")),
    AVEC_MODE_STAT=SIMP(statut="f", typ="TXM", defaut="OUI", into=("OUI", "NON")),
)
