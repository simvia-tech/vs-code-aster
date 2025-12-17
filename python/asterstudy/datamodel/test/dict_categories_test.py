# -*- coding: utf-8 -*-

# Copyright 2016 EDF R&D
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License Version 3 as
# published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, you may download a copy of license
# from https://www.gnu.org/licenses/gpl-3.0.

# pragma pylint: skip-file
# to disable 'duplicate-code' with dict_categories.py

"""
Old categories only used for unittests.
"""


from collections import OrderedDict


__all__ = ["CATEGORIES_DEFINITION", "DEPRECATED"]


CATEGORIES_DEFINITION = OrderedDict()

CATEGORIES_DEFINITION["Mesh"] = [
    "ASSE_MAILLAGE",
    "CREA_MAILLAGE",
    "DEFI_GROUP",
    "MODI_MAILLAGE",
    "LIRE_MAILLAGE",
    ]

CATEGORIES_DEFINITION["Model Definition"] = [
    "AFFE_CARA_ELEM",
    "AFFE_MODELE",
    "DEFI_BASE_REDUITE",
    "DEFI_DOMAINE_REDUIT",
    "DEFI_GEOM_FIBRE",
    "MACR_CARA_POUTRE",
    "MODI_MODELE",
    ]

CATEGORIES_DEFINITION["Material"] = [
    "AFFE_MATERIAU",
    "CREA_LIB_MFRONT",
    "DEFI_COMPOSITE",
    "DEFI_GLRC",
    "DEFI_MATER_GC",
    "DEFI_MATERIAU",
    "DEFI_TRC",
    "INCLUDE_MATERIAU",
    ]

CATEGORIES_DEFINITION["Functions and Lists"] = [
    "CALC_FONCTION",
    "CALC_FONC_INTERP",
    "CALC_TABLE",
    "CREA_TABLE",
    "DEFI_CONSTANTE",
    "DEFI_FONCTION",
    "DEFI_LIST_FREQ",
    "DEFI_LIST_INST",
    "DEFI_LIST_REEL",
    "DEFI_NAPPE",
    "FORMULE",
    "LIRE_FONCTION",
    "LIRE_TABLE",
    ]

CATEGORIES_DEFINITION["BC and Load"] = [
    "AFFE_CHAR_CINE",
    "AFFE_CHAR_CINE_F",
    "AFFE_CHAR_MECA",
    "AFFE_CHAR_MECA_C",
    "AFFE_CHAR_MECA_F",
    "AFFE_CHAR_THER",
    "AFFE_CHAR_THER_F",
    "CALC_CHAR_SEISME",
    "DEFI_CABLE_BP",
    "DEFI_CONTACT",
    "DEFI_FLUI_STRU",
    "DEFI_FONC_ELEC",
    "DEFI_FONC_FLUI",
    "DEFI_OBSTACLE",
    ]

CATEGORIES_DEFINITION["Pre Analysis"] = [
    "ASSEMBLAGE",
    "CALC_AMOR_MODAL",
    "CALC_CHAM_FLUI",
    "COMB_MATR_ASSE",
    "DEFI_BASE_MODALE",
    "GENE_ACCE_SEISME",
    "INFO_MODE",
    "MACRO_MATR_AJOU",
    "MODE_NON_LINE",
    "PROJ_BASE",
    "PROJ_CHAMP",
    ]

CATEGORIES_DEFINITION["Analysis"] = [
    "CALC_ESSAI_GEOMECA",
    "CALC_FLUI_STRU",
    "CALC_META",
    "CALC_MISS",
    "CALC_MODES",
    "CALC_PRECONT",
    "COMB_SISM_MODAL",
    "DYNA_NON_LINE",
    "DYNA_VIBRA",
    "MECA_STATIQUE",
    "MODE_STATIQUE",
    "SIMU_POINT_MAT",
    "STAT_NON_LINE",
    "THER_LINEAIRE",
    "THER_NON_LINE",
    "THER_NON_LINE_MO",
    ]

CATEGORIES_DEFINITION["Post Processing"] = [
    "CALC_CHAMP",
    "CALC_ERREUR",
    "CALC_FERRAILLAGE",
    "CALC_PRESSION",
    "CREA_CHAMP",
    "INFO_FONCTION",
    "MACR_ADAP_MAIL",
    "MACR_LIGN_COUPE",
    "MODI_REPERE",
    "POST_CHAMP",
    "POST_ELEM",
    "POST_GENE_PHYS",
    "POST_RELEVE_T",
    "REST_GENE_PHYS",
    "REST_REDUIT_COMPLET",
    "REST_SPEC_PHYS",
    "REST_SPEC_TEMP",
    ]

CATEGORIES_DEFINITION["Fracture and Fatigue"] = [
    "CALC_FATIGUE",
    "CALC_G",
    "CALC_GP",
    "DEFI_FISS_XFEM",
    "DEFI_FOND_FISS",
    "MODI_MODELE_XFEM",
    "POST_CHAM_XFEM",
    "POST_CZM_FISS",
    "POST_FATIGUE",
    "POST_K1_K2_K3",
    "POST_K_BETA",
    "POST_K_TRANS",
    "POST_MAIL_XFEM",
    "POST_RCCM",
    "POST_RUPTURE",
    "PROPA_FISS",
    "RAFF_GP",
    "RAFF_XFEM",
    "RECA_WEIBULL",
    ]

CATEGORIES_DEFINITION["Output"] = [
    "CREA_RESU",
    "EXTR_MODE",
    "EXTR_RESU",
    "EXTR_TABLE",
    "IMPR_FONCTION",
    "IMPR_RESU",
    "IMPR_RESU_SP",
    "IMPR_TABLE",
    "RECU_FONCTION",
    "RECU_TABLE",
    ]

DEPRECATED = [
    "DEBUT",
    "DEFI_FICHIER",
    "INCLUDE",
    "FIN",
    "POURSUITE",
    ]
