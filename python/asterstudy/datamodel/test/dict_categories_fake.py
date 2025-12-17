# -*- coding: utf-8 -*-

# Copyright 2016-2018 EDF R&D
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
Fake categories only used for tests.
"""


from collections import OrderedDict


__all__ = ["CATEGORIES_DEFINITION", "DEPRECATED"]


CATEGORIES_DEFINITION = OrderedDict()

CATEGORIES_DEFINITION["Category"] = [
    "ASSE_MAILLAGE",
    "CREA_MAILLAGE",
    ("Sub-category 1", [
            "DEFI_GROUP",
            "MODI_MAILLAGE",
            ]),
    "LIRE_MAILLAGE",
    ("Sub-category 2", [
            "AFFE_CARA_ELEM",
            ]),
    ("Sub-category 1", [
            "AFFE_MODELE",
            ]),
    "DEFI_BASE_REDUITE",
    "DEFI_DOMAINE_REDUIT",
    "DEFI_GEOM_FIBRE",
    ("Sub-category 2", [
            "MACR_CARA_POUTRE",
            "MODI_MODELE",
            ]),
    ]

DEPRECATED = [
    ]
