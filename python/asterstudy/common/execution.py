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
Utilities about executions
--------------------------

Some utilities for executions.

"""


import os
import re

from .base_utils import no_new_attributes

CMDTAG = re.compile(r"\.\. __(?P<orig>run|stg)(?P<stgnum>[0-9]+)_"
                    r"(?P<loc>cmd|txt)(?P<id>[0-9]+(:[0-9]+)?)")


class MPIPrefix:
    """Object to deal with prefixes added during MPI executions.

    Arguments:
        proc0 (bool): Tell if the first processor is included in the
            expressions (default: *True*).
    """
    # Regular expressions for MPI prefixes
    _expr = (
        r'^\[[{init}-9][0-9]*\] ?',  # IntelMPI
        r'^\[[0-9]+, *[{init}-9][0-9]*\]<std...>:?', # OpenMPI
    )

    proc0 = expr = expr_c = None
    __setattr__ = no_new_attributes(object.__setattr__)

    def __init__(self, proc0=True):
        self.proc0 = proc0

        init = 0 if proc0 else 1
        self.expr = [i.format(init=init) for i in MPIPrefix._expr]
        self.expr_c = tuple(re.compile(i) for i in self.expr)

    @property
    def regexp(self):
        """Return the regular expressions."""
        return self.expr

    @property
    def regexp_c(self):
        """Return the compiled regular expressions."""
        return self.expr_c


def remove_mpi_prefix(text):
    """Remove the MPI prefix in the log of code_aster execution.

    Arguments:
        text(str): Log (output) of code_aster execution.

    Returns:
        str: Log without MPI prefix.
    """
    mpi_prefix = MPIPrefix(proc0=True)

    def _clean(line):
        for expr in mpi_prefix.regexp_c:
            line = expr.sub("", line)
        return line

    lines = [_clean(line) for line in text.splitlines()]
    return os.linesep.join(lines)
