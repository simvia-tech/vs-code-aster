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

# person_in_charge: olivier.boiteau at edf.fr

from ..Commons import *
from ..Language.DataStructure import *
from ..Language.Syntax import *

INFO_MODE = OPER(
    nom="INFO_MODE",
    op=32,
    sd_prod=table_sdaster,
    fr=tr("Calculer, imprimer, et sauvegarder le nombre de valeurs propres dans un contour donné"),
    TYPE_MODE=SIMP(
        statut="f",
        typ="TXM",
        defaut="DYNAMIQUE",
        into=("MODE_COMPLEXE", "DYNAMIQUE", "MODE_FLAMB", "GENERAL"),
        fr=tr("Type d analyse"),
    ),
    INFO=SIMP(statut="f", typ="I", defaut=1, into=(1, 2)),
    b_dynamique=BLOC(
        condition="""equal_to("TYPE_MODE", 'DYNAMIQUE')""",
        fr=tr("Recherche du nombre de fréquences propres"),
        MATR_RIGI=SIMP(
            statut="o",
            typ=(
                matr_asse_depl_r,
                matr_asse_temp_r,
                matr_asse_pres_r,
                matr_asse_gene_r,
                matr_asse_depl_c,
                matr_asse_gene_c,
            ),
        ),
        MATR_MASS=SIMP(
            statut="o", typ=(matr_asse_depl_r, matr_asse_temp_r, matr_asse_pres_r, matr_asse_gene_r)
        ),
        FREQ=SIMP(
            statut="o",
            typ="R",
            min=2,
            max="**",
            validators=AndVal((OrdList("croissant"), NoRepeat())),
            fr=tr("Liste de frequences"),
        ),
        COMPTAGE=FACT(
            statut="d",
            METHODE=SIMP(statut="f", typ="TXM", defaut="AUTO", into=("AUTO", "STURM")),
            SEUIL_FREQ=SIMP(statut="f", typ="R", defaut=1.0e-2),
            PREC_SHIFT=SIMP(statut="f", typ="R", defaut=5.0e-2),
            NMAX_ITER_SHIFT=SIMP(statut="f", typ="I", defaut=3, val_min=0),
        ),
    ),
    b_flambement=BLOC(
        condition="""equal_to("TYPE_MODE", 'MODE_FLAMB')""",
        fr=tr("Recherche du nombre de charges critiques"),
        MATR_RIGI=SIMP(
            statut="o",
            typ=(
                matr_asse_depl_r,
                matr_asse_temp_r,
                matr_asse_pres_r,
                matr_asse_gene_r,
                matr_asse_depl_c,
                matr_asse_gene_c,
            ),
        ),
        MATR_RIGI_GEOM=SIMP(
            statut="o", typ=(matr_asse_depl_r, matr_asse_temp_r, matr_asse_pres_r, matr_asse_gene_r)
        ),
        CHAR_CRIT=SIMP(
            statut="o",
            typ="R",
            min=2,
            max="**",
            validators=AndVal((OrdList("croissant"), NoRepeat())),
            fr=tr("Liste de charges critiques"),
        ),
        COMPTAGE=FACT(
            statut="d",
            METHODE=SIMP(statut="f", typ="TXM", defaut="AUTO", into=("AUTO", "STURM")),
            SEUIL_CHAR_CRIT=SIMP(statut="f", typ="R", defaut=1.0e-2),
            PREC_SHIFT=SIMP(statut="f", typ="R", defaut=5.0e-2),
            NMAX_ITER_SHIFT=SIMP(statut="f", typ="I", defaut=3, val_min=0),
        ),
    ),
    b_complexe=BLOC(
        condition="""equal_to("TYPE_MODE", 'MODE_COMPLEXE')""",
        fr=tr("Recherche du nombre de fréquences propres"),
        MATR_RIGI=SIMP(
            statut="o",
            typ=(
                matr_asse_depl_r,
                matr_asse_temp_r,
                matr_asse_pres_r,
                matr_asse_gene_r,
                matr_asse_depl_c,
                matr_asse_gene_c,
            ),
        ),
        MATR_MASS=SIMP(
            statut="o", typ=(matr_asse_depl_r, matr_asse_temp_r, matr_asse_pres_r, matr_asse_gene_r)
        ),
        MATR_AMOR=SIMP(
            statut="f", typ=(matr_asse_depl_r, matr_asse_temp_r, matr_asse_pres_r, matr_asse_gene_r)
        ),
        TYPE_CONTOUR=SIMP(statut="f", typ="TXM", defaut="CERCLE", into=("CERCLE", "CERCLE")),
        RAYON_CONTOUR=SIMP(statut="o", typ="R", val_min=1.0e-2),
        CENTRE_CONTOUR=SIMP(statut="f", typ="C", defaut=0.0 + 0.0j),
        COMPTAGE=FACT(
            statut="d",
            METHODE=SIMP(statut="f", typ="TXM", defaut="AUTO", into=("AUTO", "APM")),
            NBPOINT_CONTOUR=SIMP(statut="f", typ="I", defaut=40, val_min=10, val_max=1000),
            NMAX_ITER_CONTOUR=SIMP(statut="f", typ="I", defaut=3, val_min=1, val_max=5),
        ),
    ),
    b_general=BLOC(
        condition="""equal_to("TYPE_MODE", 'GENERAL')""",
        fr=tr("Recherche du nombre de valeurs propres"),
        MATR_A=SIMP(
            statut="o",
            typ=(
                matr_asse_depl_r,
                matr_asse_temp_r,
                matr_asse_pres_r,
                matr_asse_gene_r,
                matr_asse_depl_c,
                matr_asse_gene_c,
            ),
        ),
        MATR_B=SIMP(
            statut="o", typ=(matr_asse_depl_r, matr_asse_temp_r, matr_asse_pres_r, matr_asse_gene_r)
        ),
        MATR_C=SIMP(
            statut="f", typ=(matr_asse_depl_r, matr_asse_temp_r, matr_asse_pres_r, matr_asse_gene_r)
        ),
        CHAR_CRIT=SIMP(
            statut="f",
            typ="R",
            min=2,
            max="**",
            validators=AndVal((OrdList("croissant"), NoRepeat())),
            fr=tr("Liste de charges critiques"),
        ),
        b_contour=BLOC(
            condition="""not exists("CHAR_CRIT")""",
            TYPE_CONTOUR=SIMP(statut="f", typ="TXM", defaut="CERCLE", into=("CERCLE", "CERCLE")),
            RAYON_CONTOUR=SIMP(statut="o", typ="R", val_min=1.0e-2),
            CENTRE_CONTOUR=SIMP(statut="f", typ="C", defaut=0.0 + 0.0j),
        ),
        COMPTAGE=FACT(
            statut="d",
            METHODE=SIMP(statut="f", typ="TXM", defaut="AUTO", into=("AUTO", "STURM", "APM")),
            SEUIL_CHAR_CRIT=SIMP(statut="f", typ="R", defaut=1.0e-2),
            PREC_SHIFT=SIMP(statut="f", typ="R", defaut=5.0e-2),
            NMAX_ITER_SHIFT=SIMP(statut="f", typ="I", defaut=3, val_min=0),
        ),
        NBPOINT_CONTOUR=SIMP(statut="f", typ="I", defaut=40, val_min=10, val_max=1000),
        NMAX_ITER_CONTOUR=SIMP(statut="f", typ="I", defaut=3, val_min=1, val_max=5),
    ),
    TITRE=SIMP(statut="f", typ="TXM"),
    # -------------------------------------------------------------------
    #        Catalogue commun SOLVEUR
    SOLVEUR=C_SOLVEUR("INFO_MODE"),
    #        Mot-cle pour piloter les niveaux de parallelismes de l'operateur (a ne pas confondre avec le mot-cle
    #        cache PARALLELISME_MACRO)
    NIVEAU_PARALLELISME=SIMP(statut="f", typ="TXM", defaut="COMPLET", into=("PARTIEL", "COMPLET")),
    # -------------------------------------------------------------------
    # -------------------------------------------------------------------
    #  Mot-cles caches pour activer le parallelisme au sein d'une macro-commande
    PARALLELISME_MACRO=FACT(
        statut="d",
        TYPE_COM=SIMP(
            statut="c", typ="I", defaut=-999, into=(-999, 1, 2), fr=tr("Type de communication")
        ),
    ),
    # -------------------------------------------------------------------
)
