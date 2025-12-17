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

# person_in_charge: mathieu.courtois@edf.fr

"""
Define a parameter used in a parametric or probabilistic study.

The parameters are provided as a pickle file that contains:
- the list of the parameters names,
- the list of the parameters values.
"""


import os.path as osp
import pickle

import numpy


class VariableSupport:
    """Implementation of the VARIABLE feature for parametic study."""

    nom = "VARIABLE"  # for vocab01a
    inputs_filename = "inputs.pick"

    def __init__(self):
        """Initialization"""
        self._cache = None

    def _get_inputs(self):
        """Read the input file and store content in cache for future calls."""
        if self._cache is not None:
            return self._cache

        if not osp.exists(self.inputs_filename):
            print("No such file: '{0}'".format(self.inputs_filename))
            params, values = [], []
        else:
            print("Settings variables values...")
            with open("inputs.pick", "rb") as pick:
                params = pickle.load(pick, encoding="latin1")
                values = pickle.load(pick, encoding="latin1")

        self._cache = params, values
        assert len(params) == len(values), (params, values)
        return self._cache

    def __call__(self, NOM_PARA, VALE):
        """Return the value of a parameter.

        If the parameter is not provided by the pickle file, the returned value is
        the nominal one.

        Arguments:
            NOM_PARA (str): Name of the parameter.
            VALE (float): Nominal value of the parameter.

        Returns:
            float: Value of the parameter.
        """
        params, values = self._get_inputs()
        inputs = dict(list(zip(params, values)))
        value = inputs.get(NOM_PARA)
        if value is None:
            value = VALE
            print("- Use nominal value for {0} = {1}".format(NOM_PARA, value))
        else:
            print("- From inputs file for  {0} = {1}".format(NOM_PARA, value))
        return value


VARIABLE = VariableSupport()
