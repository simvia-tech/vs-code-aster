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

from ..Language.DataStructure import *
from ..Language.Syntax import *


def C_NOM_DDL_INTO(phenomene, with_dnor=None, select_dof=None):
    assert phenomene in ("MECANIQUE", "THERMIQUE"), "unsupported command: {0}".format(phenomene)

    if phenomene == "MECANIQUE":
        if select_dof is None:
            dof_name = [
                "DX",
                "DY",
                "DZ",
                "DRX",
                "DRY",
                "DRZ",
                "PRES",
                "PHI",
                "GONF",
                "TEMP",
                "PRE1",
                "PRE2",
                "GRX",
                "DRGX",
                "DRGY",
                "DRGZ",
                "PSI",
                "UI2",
                "UI3",
                "VI2",
                "VI3",
                "WI2",
                "WI3",
                "UO2",
                "UO3",
                "VO2",
                "VO3",
                "WO2",
                "WO3",
                "UI4",
                "UI5",
                "VI4",
                "VI5",
                "WI4",
                "WI5",
                "UO4",
                "UO5",
                "VO4",
                "VO5",
                "WO4",
                "WO5",
                "UI6",
                "UO6",
                "VI6",
                "VO6",
                "WI6",
                "WO6",
                "WO",
                "WI1",
                "WO1",
                "H1X",
                "H1Y",
                "H1Z",
                "H1PRE1",
                "K1",
                "K2",
                "K3",
                "V11",
                "V12",
                "V13",
                "V21",
                "V22",
                "V23",
                "V31",
                "V32",
                "V33",
                "PRES11",
                "PRES12",
                "PRES13",
                "PRES21",
                "PRES22",
                "PRES23",
                "PRES31",
                "PRES32",
                "PRES33",
                "LH1",
                "GLIS",
            ]
        elif select_dof == "DEPL":
            dof_name = ["DX", "DY", "DZ", "DRX", "DRY", "DRZ"]
        else:
            assert False

    elif phenomene == "THERMIQUE":
        dof_name = ["TEMP", "TEMP_MIL", "TEMP_INF", "TEMP_SUP", "H1"]

    dnor_name = ["DNOR"]

    if with_dnor is not None:
        return tuple(dof_name + dnor_name)
    else:
        return tuple(dof_name)
