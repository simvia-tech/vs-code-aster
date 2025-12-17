# -*- coding: utf-8 -*-

# Copyright 2021 EDF R&D
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

"""Configuration files for AsterStudy Results tab"""

WARP_READY_FIELDS = ['DEPL', 'DEPL_ABSOLU']
VECTOR_READY_FIELDS = ['DEPL', 'VITE', 'ACCE',
                       'DEPL_ABSOLU', 'VITE_ABSOLU', 'ACCE_ABSOLU',
                       'REAC_NODA', 'FORC_NODA',
                       '.REPLO_1', '.REPLO_2', '.REPLO_3',
                       '_X', '_Y', '_Z']

FIELDS_WITH_MAG = VECTOR_READY_FIELDS + []

TRANSLATIONAL_COMPS = ['DX', 'DY', 'DZ', 'X', 'Y', 'Z']

REPRESENTATIONS = ['Points',
                   'Wireframe',
                   'Surface',
                   'Surface With Edges']

FIELD_LABELS = {'DEPL': 'Displacement',
                'VITE': 'Velocity',
                'ACCE': 'Acceleration',
                'TEMP': 'Temperature',
                'REAC_NODA': 'Support reaction forces/moments',
                'FORC_NODA': 'Nodal forces/moments',
                'EFGE_ELNO': 'Structural forces/moments (nodes)',
                'EFGE_ELGA': 'Structural forces/moments (integration pts)',
                'EFGE_NOEU': 'Structural forces/moments (interpolated)',
                'SIEF_ELGA': 'Elementary stress (integration pts)',
                'SIEF_ELNO': 'Elementary stress (nodes)',
                'SIEF_NOEU': 'Elementary stress (interpolated)',
                'SIGM_ELGA': 'Global stress (integration pts)',
                'SIGM_ELNO': 'Global stress (nodes)',
                'SIGM_NOEU': 'Global stress (interpolated)',
                'SIPM_ELNO': 'Beam elements min/max stress (nodes)',
                'SIPM_NOEU': 'Beam elements min/max stress (interpolated)',
                'SIPO_ELNO': 'Beam elements stress (nodes)',
                'SIPO_NOEU': 'Beam elements stress (interpolated)',
                'EPSI_ELGA': 'Elementary strain (integration pts)',
                'EPSI_ELNO': 'Elementary strain (nodes)',
                'EPSI_NOEU': 'Elementary strain (interpolated)',
                'EPEQ_ELGA': 'Equivalent strain (integration pts)',
                'EPEQ_ELNO': 'Equivalent strain (nodes)',
                'EPEQ_NOEU': 'Equivalent strain (interpolated)',
                'SIEQ_ELGA': 'Equivalent stress (integration pts)',
                'SIEQ_ELNO': 'Equivalent stress (nodes)',
                'SIEQ_NOEU': 'Equivalent stress (interpolated)',
                'CONT_ELEM': 'Contact pressure and properties',
                'VARI_ELGA': 'Constitutive-law\'s variables (indexed components)',
                'VARI_ELGA_NOMME': 'Constitutive-law\'s variables (named components)',
                'STRX_ELGA': 'Forces/displacements for structural elements',
                'FamilyIdNode': 'Nodal group identifiers',
                'FamilyIdCell': 'Element group identifiers',
                'NumIdCell': 'Element numbering',
                '.REPLO_1': 'Element frame axis-1 (LOC-X)',
                '.REPLO_2': 'Element frame axis-2 (LOC-Y)',
                '.REPLO_3': 'Element frame axis-3 (LOC-Z)',
                '_X': 'Element frame axis-1 (LOC-X) on nodes',
                '_Y': 'Element frame axis-2 (LOC-Y) on nodes',
                '_Z': 'Element frame axis-3 (LOC-Z) on nodes',
                'FERR_ELEM': 'Reinforcement area',
                }

_SUFFICES = ['ELNO', 'ELGA', 'NOEU']
_INFOS = ['on nodes, per element', 'on elements', 'on nodes']
for _i in range(1, 11):
    _LBL = 'UT{:02d}_'.format(_i)
    for _j, _sffx in enumerate(_SUFFICES):
        FIELD_LABELS[
            _LBL + _sffx] = 'User-defined field #{} ({})'.format(_i, _INFOS[_j])

del _INFOS, _LBL, _SUFFICES

MESH_FIELDS = ['FamilyIdNode', 'FamilyIdCell', 'NumIdCell']

# Default values for the display properties, as a function of the
# MAXIMUM mesh dimension, 0 = 0D elements, 1 = 1D elements, etc.
DISPLAY_PROPS_DEFAULTS = [
    {'Representation': 'Points', 'Ambient' : 0.60, 'LineWidth': 0.0, 'PointSize': 8.0},
    {'Representation': 'Wireframe', 'Ambient' : 0.60, 'LineWidth': 4.0, 'PointSize': 8.0},
    {'Representation': 'Surface With Edges', 'Ambient' : 0.60, 'LineWidth': 1.0, 'PointSize': 4.0},
    {'Representation': 'Surface', 'Ambient' : 0.15, 'LineWidth': 1.0, 'PointSize': 2.0}]
for dprop in DISPLAY_PROPS_DEFAULTS:
    dprop.update({'Opacity': 1.0, 'Interpolation' : 'Flat'})

RESULTS_PV_LAYOUT_NAME = str('AsterStudy Results Layout')
RESULTS_PV_VIEW_NAME = str('AsterStudy Results View')

DEBUG = False
GROUPS_FILTER_LIMIT = 5000
