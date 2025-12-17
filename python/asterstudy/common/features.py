# -*- coding: utf-8 -*-

# Copyright 2017 - 2019 EDF R&D
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

"""
Features
--------

The module defines an object to manage the feature supported by a code_aster
version.
"""

import os
from .base_utils import no_new_attributes


class Features:
    """Object that holds the supported features.

    Arguments:
        vers (tuple[int]): Version number as a tuple (ex: (14, 4, 0)).
            Defaults to the most possible recent version.
    """

    _support = None
    __setattr__ = no_new_attributes(object.__setattr__)

    def __init__(self, vers=None):
        """Initialization."""
        self._support = {}
        vers = vers or (99,)
        _test_ = int(os.getenv('ASTERSTUDY_WITHIN_TESTS', '0'))
        # < 14.1.4 or < 13.5.3: do not export Command ids
        enabled = vers >= (14, 1, 4) or (vers[0] == 13 and vers >= (13, 5, 3))
        self._support["command_ids"] = enabled
        # parametric studies supported starting at 14.1.11 and 13.5.8
        enabled = vers >= (14, 1, 11) or (vers[0] == 13 and vers >= (13, 5, 8))
        self._support["parametric"] = enabled
        # get_all_types only exist starting at 14.1.14 and 13.5.9
        enabled = vers >= (14, 1, 14) or (vers[0] == 13 and vers >= (13, 5, 8))
        self._support["all_types"] = enabled
        # definition of formulas dependencies supported starting at 14.1.13
        enabled = vers >= (14, 1, 13) or _test_
        self._support["formula_deps"] = enabled
        # full python: (>= 15.2) results names longer than 8 chars
        enabled = vers >= (15, 2, 0)
        self._support["full_python"] = enabled
        # simplified DETRUIRE syntax >= 15.3.3
        enabled = vers >= (15, 3, 3)
        self._support["simplified_del"] = enabled
        # catalog with compat_syntax functions for >= 15.3.24
        enabled = vers >= (15, 3, 24)
        self._support["compat_syntax"] = enabled
        # use run_aster for >= 15.4.0
        enabled = vers >= (15, 4, 0)
        self._support["use_run_aster"] = enabled

    def __getitem__(self, key):
        """Tell if a feature is supported.

        Returns:
            bool: *True* if supported, *False* if not, raise KeyError for
            unknown feature.
        """
        return self._support[key]
