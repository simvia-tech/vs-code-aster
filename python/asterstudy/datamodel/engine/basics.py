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

"""
Basic utilities
---------------

This module provides basic helper functions.

"""

import re


def version_ismpi(version):
    """Tell if the version is a MPI version (currently by name convention).

    Arguments:
        version (str): Version name.

    Returns:
        bool: *True* if the version supports MPI, *False* otherwise.
    """
    return bool(version) and re.search('_mpi', version, flags=re.I) is not None
