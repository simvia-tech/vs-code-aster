# -*- coding: utf-8 -*-

# Copyright 2019 EDF R&D
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

"""Main files for AsterStudy integrated post-processing module"""

from .config import *
from .representation import (BaseRep, ColorRep, ContourRep, LocalFrameRep,
                             ModesRep, VectorRep, WarpRep)
from .result_data import ConceptField, ResultConcept, ResultFile
from .utils import (clear_pipeline, create_axes, dbg_print,
                    get_active_selection, get_pv_mem_use, is_locframe,
                    is_quadratic, pvcontrol,
                    selection_plot, selection_probe, show_min_max)
