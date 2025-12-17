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

# person_in_charge: jean-luc.flejou at edf.fr

from ..Commons import *
from ..Language.DataStructure import *
from ..Language.Syntax import *

DEFI_MATER_GC = MACRO(
    nom="DEFI_MATER_GC",
    op=OPS("code_aster.MacroCommands.defi_mater_gc_ops.defi_mater_gc_ops"),
    sd_prod=mater_sdaster,
    reentrant="n",
    fr=tr("Définir des lois matériaux spécifique au Génie Civil"),
    #
    regles=(UN_PARMI("MAZARS", "ACIER", "ENDO_FISS_EXP", "ENDO_LOCA_EXP", "BETON_GLRC"),),
    #
    # ============================================================================
    MAZARS=FACT(
        statut="f",
        max=1,
        fr=tr("Paramètres matériaux de MAZARS unilatéral à partir des caractéristiques du béton"),
        CODIFICATION=SIMP(statut="o", typ="TXM", into=("ESSAI", "BAEL91", "EC2")),
        b_BAEL91=BLOC(
            condition=""" equal_to("CODIFICATION", 'BAEL91')""",
            UNITE_CONTRAINTE=SIMP(
                statut="o",
                typ="TXM",
                into=("MPa", "Pa"),
                fr=tr("Unité des contraintes du problème."),
            ),
            FCJ=SIMP(
                statut="o",
                typ="R",
                val_min=0.0e0,
                fr=tr("Contrainte au pic en compression [Unité]"),
            ),
        ),
        b_EC2=BLOC(
            condition=""" equal_to("CODIFICATION", 'EC2')""",
            UNITE_CONTRAINTE=SIMP(
                statut="o",
                typ="TXM",
                into=("MPa", "Pa"),
                fr=tr("Unité des contraintes du problème."),
            ),
            CLASSE=SIMP(
                statut="o",
                typ="TXM",
                fr=tr("Classe de résistance du béton, selon Eurocode 2"),
                into=(
                    "C12/15",
                    "C16/20",
                    "C20/25",
                    "C25/30",
                    "C30/37",
                    "C35/45",
                    "C40/50",
                    "C45/55",
                    "C50/60",
                    "C55/67",
                    "C60/75",
                    "C70/85",
                    "C80/95",
                    "C90/105",
                ),
            ),
        ),
        b_ESSAI=BLOC(
            condition=""" equal_to("CODIFICATION", 'ESSAI')""",
            regles=(PRESENT_ABSENT("EPSD0", "EPST0"),),
            b_espi=BLOC(
                condition="""exists('EPST0')""",
                EPSC0=SIMP(
                    statut="f",
                    typ="R",
                    val_min=0.0e0,
                    fr=tr("Déformation, seuil d'endommagement en compression"),
                ),
            ),
            FCJ=SIMP(
                statut="o",
                typ="R",
                val_min=0.0e0,
                fr=tr("Contrainte au pic en compression [Unité]"),
            ),
            EIJ=SIMP(statut="o", typ="R", val_min=0.0e0, fr=tr("Module d'Young [Unité]")),
            EPSI_C=SIMP(
                statut="o", typ="R", val_min=0.0e0, fr=tr("Déformation au pic en compression")
            ),
            FTJ=SIMP(
                statut="o", typ="R", val_min=0.0e0, fr=tr("Contrainte au pic en traction [Unité]")
            ),
            NU=SIMP(
                statut="f", typ="R", val_min=0.0e0, val_max=0.5e0, fr=tr("Coefficient de poisson")
            ),
            EPSD0=SIMP(
                statut="f",
                typ="R",
                val_min=0.0e0,
                fr=tr("Déformation, seuil d'endommagement en traction et compression"),
            ),
            EPST0=SIMP(
                statut="f",
                typ="R",
                val_min=0.0e0,
                fr=tr("Déformation, seuil d'endommagement en traction"),
            ),
            K=SIMP(statut="f", typ="R", val_min=0.0e0, fr=tr("Asymptote en cisaillement pur")),
            AC=SIMP(
                statut="f",
                typ="R",
                val_min=0.0e0,
                fr=tr("Paramètre de décroissance post-pic en compression"),
            ),
            BC=SIMP(
                statut="f",
                typ="R",
                val_min=0.0e0,
                fr=tr("Paramètre de décroissance post-pic en compression"),
            ),
            AT=SIMP(
                statut="f",
                typ="R",
                val_min=0.0e0,
                val_max=1.0e0,
                fr=tr("Paramètre de décroissance post-pic en traction"),
            ),
            BT=SIMP(
                statut="f",
                typ="R",
                val_min=0.0e0,
                fr=tr("Paramètre de décroissance post-pic en traction"),
            ),
            # Pour post-traitement ELS et ELU
            SIGM_LIM=SIMP(
                statut="f", typ="R", val_min=0.0e0, fr=tr("Contrainte  limite, post-traitement")
            ),
            EPSI_LIM=SIMP(
                statut="f", typ="R", val_min=0.0e0, fr=tr("Déformation limite, post-traitement")
            ),
        ),
    ),
    # ============================================================================
    BETON_GLRC=FACT(
        statut="f",
        max=1,
        fr=tr("Paramètres matériaux GLRC du béton"),
        CODIFICATION=SIMP(statut="o", typ="TXM", into=("ESSAI", "EC2")),
        b_EC2=BLOC(
            condition=""" equal_to("CODIFICATION", 'EC2')""",
            UNITE_CONTRAINTE=SIMP(
                statut="o",
                typ="TXM",
                into=("MPa", "Pa"),
                fr=tr("Unité des contraintes du problème."),
            ),
            CLASSE=SIMP(
                statut="o",
                typ="TXM",
                fr=tr("Classe de résistance du béton, selon Eurocode 2"),
                into=(
                    "C12/15",
                    "C16/20",
                    "C20/25",
                    "C25/30",
                    "C30/37",
                    "C35/45",
                    "C40/50",
                    "C45/55",
                    "C50/60",
                    "C55/67",
                    "C60/75",
                    "C70/85",
                    "C80/95",
                    "C90/105",
                ),
            ),
        ),
        b_ESSAI=BLOC(
            condition=""" equal_to("CODIFICATION", 'ESSAI')""",
            FCJ=SIMP(
                statut="o",
                typ="R",
                val_min=0.0e0,
                fr=tr("Contrainte au pic en compression [Unité]"),
            ),
            EIJ=SIMP(statut="o", typ="R", val_min=0.0e0, fr=tr("Module d'Young [Unité]")),
            EPSI_C=SIMP(
                statut="o", typ="R", val_min=0.0e0, fr=tr("Déformation au pic en compression")
            ),
            FTJ=SIMP(
                statut="o", typ="R", val_min=0.0e0, fr=tr("Contrainte au pic en traction [Unité]")
            ),
            NU=SIMP(
                statut="f",
                typ="R",
                val_min=0.0e0,
                val_max=0.5e0,
                defaut=0.2,
                fr=tr("Coefficient de poisson"),
            ),
        ),
    ),
    # ============================================================================
    ACIER=FACT(
        statut="f",
        max=1,
        fr=tr("Définir les paramètres matériaux de l'acier pour le Génie Civil"),
        E=SIMP(statut="o", typ="R", val_min=0.0e0, fr=tr("Module d'Young")),
        SY=SIMP(statut="o", typ="R", val_min=0.0e0, fr=tr("Limite élastique")),
        NU=SIMP(statut="f", typ="R", val_min=0.0e0, val_max=0.5e0, fr=tr("Coefficient de poisson")),
        D_SIGM_EPSI=SIMP(statut="f", typ="R", val_min=0.0e0, fr=tr("Module plastique")),
        # Pour post-traitement ELS et ELU
        SIGM_LIM=SIMP(
            statut="f", typ="R", val_min=0.0e0, fr=tr("Contrainte limite, post-traitement")
        ),
        EPSI_LIM=SIMP(
            statut="f", typ="R", val_min=0.0e0, fr=tr("Déformation limite, post-traitement")
        ),
    ),
    # ============================================================================
    ENDO_FISS_EXP=FACT(
        statut="f",
        max=1,
        fr=tr("Définir les paramètres matériaux du béton pour la loi ENDO_FISS_EXP"),
        regles=(UN_PARMI("P", "G_INIT"), EXCLUS("Q", "Q_REL")),
        E=SIMP(statut="o", typ="R", val_min=0.0e0, fr=tr("Module d'Young")),
        NU=SIMP(statut="o", typ="R", val_min=0.0e0, val_max=0.5e0, fr=tr("Coefficient de poisson")),
        FT=SIMP(statut="o", typ="R", val_min=0.0e0, fr=tr("Limite en traction simple")),
        FC=SIMP(statut="o", typ="R", val_min=0.0e0, fr=tr("Limite en compression simple")),
        GF=SIMP(statut="o", typ="R", val_min=0.0e0, fr=tr("Energie de fissuration")),
        P=SIMP(
            statut="f",
            typ="R",
            val_min=1.0e0,
            fr=tr("Paramètre dominant de la loi cohésive asymptotique"),
        ),
        G_INIT=SIMP(
            statut="f",
            typ="R",
            val_min=0.0,
            fr=tr("Energie de fissuration initiale de la loi cohésive asymptotique"),
        ),
        Q=SIMP(
            statut="f",
            typ="R",
            val_min=0.0e0,
            fr=tr("Paramètre secondaire de la loi cohésive asymptotique"),
        ),
        Q_REL=SIMP(
            statut="f",
            typ="R",
            val_min=0.0e0,
            val_max=1.0,
            fr=tr("Paramètre Q exprime de manière relative par rapport a Qmax(P)"),
        ),
        LARG_BANDE=SIMP(
            statut="o", typ="R", val_min=0.0e0, fr=tr("Largeur de bande d'endommagement (2*D)")
        ),
        REST_RIGI_FC=SIMP(
            statut="f",
            typ="R",
            val_min=0.0,
            val_max=0.99,
            defaut=0.9,
            fr=tr("Restauration de rigidité pour eps=fc/E (0=sans)"),
        ),
        COEF_RIGI_MINI=SIMP(
            statut="f",
            typ="R",
            val_min=0.0,
            defaut=0.0,
            fr=tr("Rigidité minimale dans la matrice tangente"),
        ),
    ),
    # ============================================================================
    ENDO_LOCA_EXP=FACT(
        statut="f",
        max=1,
        fr=tr("Définir les paramètres matériaux du béton pour la loi ENDO_LOCA_EXP"),
        E=SIMP(statut="o", typ="R", val_min=0.0e0, fr=tr("Module d'Young")),
        NU=SIMP(statut="o", typ="R", val_min=0.0e0, val_max=0.5e0, fr=tr("Coefficient de poisson")),
        FT=SIMP(statut="o", typ="R", val_min=0.0e0, fr=tr("Limite en traction simple")),
        FC=SIMP(statut="o", typ="R", val_min=0.0e0, fr=tr("Limite en compression simple")),
        GF=SIMP(statut="o", typ="R", val_min=0.0e0, fr=tr("Energie de fissuration")),
        P=SIMP(
            statut="f", typ="R", val_min=1.0e0, fr=tr("Paramètre de forme de la réponse cohésive")
        ),
        DIST_FISSURE=SIMP(
            statut="o", typ="R", val_min=0.0e0, fr=tr("Distance moyenne inter-fissures")
        ),
        REST_RIGI_FC=SIMP(
            statut="f",
            typ="R",
            val_min=0.0,
            val_max=1.00,
            defaut=0.95,
            fr=tr("Restauration de rigidité pour eps=fc/E (0=sans)"),
        ),
    ),
    # ============================================================================
    INFO=SIMP(statut="f", typ="I", into=(1, 2), defaut=1),
    RHO=SIMP(statut="f", typ="R", fr=tr("Masse volumique")),
    ALPHA=SIMP(statut="f", typ="R", fr=tr("Coefficient de dilatation")),
    AMOR_ALPHA=SIMP(statut="f", typ="R"),
    AMOR_BETA=SIMP(statut="f", typ="R"),
    AMOR_HYST=SIMP(statut="f", typ="R"),
)
