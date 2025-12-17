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

from ..Language.DataStructure import *
from ..Language.Syntax import *


def C_PARA_FONCTION():
    return (  # COMMUN#
        "DX",
        "DY",
        "DZ",
        "DRX",
        "DRY",
        "DRZ",
        "DTAN",
        "TEMP",
        "TSEC",
        "INST",
        "X",
        "Y",
        "Z",
        "EPSI",
        "META",
        "FREQ",
        "PULS",
        "DSP",
        "AMOR",
        "ABSC",
        "SIGM",
        "HYDR",
        "SECH",
        "PORO",
        "SAT",
        "IRRA",
        "PGAZ",
        "PCAP",
        "PLIQ",
        "PVAP",
        "PAD",
        "VITE",
        "ENDO",
        "NORM",
        "EPAIS",
        "EXCENT",
        "NEUT1",
        "NEUT2",
        "NEUT3",
        "NEUT4",
        "XF",
        "YF",
        "ZF",
        "NUME_ORDRE",
    )
