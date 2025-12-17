# -*- coding: utf-8 -*-

# Copyright 2023 EDF R&D
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
ColorRep: parent class for all colored representations
"""

import os.path as osp

from ..config import (DISPLAY_PROPS_DEFAULTS, FIELDS_WITH_MAG,
                      TRANSLATIONAL_COMPS, VECTOR_READY_FIELDS)
from ..utils import (get_array_range, get_full_array_range, is_locframe,
                     nb_points_cells)
from .base_rep import BaseRep


class ColorRep(BaseRep):
    """ColorRep implementation."""

    name = 'Colored Representation'
    base_source = None

    def defaults(self):
        """
        Add default options to self.opts, called after initialization
        and prior to the represent function
        """
        BaseRep.defaults(self)
        if 'Component' not in self.opts:
            if len(self.field.info['components']) > 1:
                if self.field.name in FIELDS_WITH_MAG:
                    self.opts['Component'] = 'Magnitude'
                else:
                    self.opts['Component'] = self.field.info['components'][0]
            else:
                self.opts['Component'] = self.field.info['components'][0]

        if 'Slice' not in self.opts:
            self.opts['Slice'] = 'None'
            self.opts['SlicePosition'] = 0.5

        if 'ColorBarAuto' not in self.opts:
            self.opts['ColorBarAuto'] = 'Automatic: current step'

        if 'ColorBarMin' not in self.opts:
            self.opts['ColorBarMin'] = 0.

        if 'ColorBarMax' not in self.opts:
            self.opts['ColorBarMax'] = 1.

        if 'ColorBarType' not in self.opts:
            self.opts['ColorBarType'] = 'Continuous'

        if 'ColorBarCategorical' not in self.opts:
            self.opts['ColorBarCategorical'] = {}

        # Remove (out)herited, unnecessary options
        if self.__class__ == ColorRep:
            if 'ColorField' in self.opts:
                self.opts.pop('ColorField', None)

            if 'ScaleFactor' in self.opts:
                self.opts.pop('ScaleFactor', None)

        self.opt_groups.update(
            {'Representation': ['Component', 'Slice', 'SlicePosition']})
        self.opt_groups.update(
            {'Color bar': ['Title', 'Unit', 'ColorBarType', 'ColorBarAuto',
                           'ColorBarMin', 'ColorBarMax', 'ColorBarCategorical']})

    def represent(self):
        """
        Provide a simple color representation of a given field.

        Special treatments (using a calculator filter):
        - DEPL, VITE, ACCE : magnitude for structural elements
                             (more than 3 components)
        - SIEF_ELGA : magnitude of the principal stresses
        """
        import pvsimple as pvs

        # Special treatment for some fields where the source
        # needs to be overloaded (DEPL for structural elements,
        # _EL* fields, etc.)
        self.customize_source()

        # Create a PV display based on the read source
        self.display = pvs.Show(self.source, self.ren_view)
        self.display.Pickable = 1

        self.update_colorbar()
        self.update_display_props(DISPLAY_PROPS_DEFAULTS[0])

    def update(self, mod_opts):
        """
        Update the colored field representation based on changes
        in the diplay options (representation support or opacity)
        """
        import pvsimple as pvs

        # This ensures that the previous representation is removed
        # along with its scalebars and other customizations
        pvs.HideAll(self.ren_view)
        pvs.HideUnusedScalarBars()

        self.update_source(mod_opts)
        self.display = pvs.Show(self.source, self.ren_view)

        # If the component changes, the colorbar title needs to be updated!
        if 'Component' in mod_opts:
            self.opts.pop('Title', None)

        # cba = ('ColorBarAuto' in mod_opts)
        # self.update_colorbar(timechange=not(cba))
        self.update_colorbar()

    def update_source(self, mod_opts):
        """
        Updates the source if necessary
        """
        import pvsimple as pvs
        if 'Component' in mod_opts:
            # Since Magnitude is explicitely calculated by
            # using a Calculator filter, we need to change
            # the source if the user requests Magnitude or
            # if the request changes from Magnitude to any
            # other component of the same field
            if (mod_opts['Component'] == 'Magnitude' or
                    self.opts['Component'] == 'Magnitude'):
                # Reset PV source (pipeline node) AND array name
                # Then call the source customizer function
                # Required for DEPL VITE ACCE and SIEF_*
                self.source = self.field.concept.result.source
                self.array = self.field.info['pv-aident']
                pvs.SetActiveSource(self.source)
                self.customize_source()

        if 'Slice' in mod_opts or 'SlicePosition' in mod_opts:
            self.update_slice()
        else:
            if self.opts['Slice'] != 'None':
                BaseRep.show_reference(self)

    def customize_source(self):
        """
        Overload the default source by using :
        - Calculator filter for DEPL, VITE, ACCE to calculate the
          field translational magnitudes for structural elements
        - Calculator filter for principal stress magnitude
          calculation.
        - Interpolation of element fields (intergration pts) _EL*

        This method modifies the representation's self.source but
        not the default one which is still conserved in

        self.field.concept.result.source

        and corresponds to the MEDReader node of paraview pipeline
        """
        import pvsimple as pvs

        colcomp = str(self.opts['Component']
                      if 'Component' in self.opts else 'Magnitude')

        new_source = None

        # group_filter is only used for ELNA and ELGO fields representation
        # with group filtering
        group_filter = []
        if self.opts['GroupsFilter']:
            group_filter = [gr[0] for gr in self.opts['GroupsFilterOptions']
                            if gr[1]]

        result = self.field.concept.result
        if self.field.info['disc'] == 'GSSNE':
            # ELNO, output is a POINTS field
            new_source = BaseRep.register_source(
                'ELNOfieldToSurface', result.full_source, ShrinkFactor=1.0,
                label='<{}:{}> TO POINTS'.format(self.field.concept.name, self.field.name))
            new_source.UpdatePipeline()

        elif self.field.info['disc'] == 'GAUSS':
            # ELGA, output is a CELLS field
            new_source = BaseRep.register_source(
                'ELGAfieldToSurface', result.full_source,
                label='<{}:{}> TO CELLS'.format(self.field.concept.name, self.field.name))
            new_source.UpdatePipeline()
            nbp, nbc = nb_points_cells(new_source)
            if nbp * nbc == 0:
                new_source = BaseRep.register_source(
                    'ELGAfieldToSurfacecellaveraged', self.source,
                    Max=0, Min=0, label='<{}:{}> TO CELLS - AVERAGED'.format(
                        self.field.concept.name, self.field.name))
                new_source.UpdatePipeline()
                self.array = self.field.info['pv-aident'] + '_avg'

        if result.quadratic:
            input_source = new_source if new_source else self.source
            pvs.SetActiveSource(input_source)

            linearized = BaseRep.register_source(
                'QuadraticToLinear', input_source,
                label='<{}> QUAD. TO LINEAR'.format(osp.basename(result.path)))
            linearized.UpdatePipeline()
            if nb_points_cells(linearized)[0] > 0:
                new_source = linearized
            else:
                result.quadratic = False

        if is_locframe(self.field) and self.field.name.startswith('.REPLO'):
            input_source = new_source if new_source else self.source
            pvs.SetActiveSource(input_source)

            # Apply a CellCenters filter for local frame fields (IMPR_CONCEPT)
            point_source = BaseRep.register_source('CellCenters',
                                            input_source, VertexCells=1,
                                            label='<{0}> CELL CENTERS'.format(
                                                self.field.concept.name))

            point_source.UpdatePipeline()
            new_source = point_source
            self.field.info['support'] = 'POINTS'

        if (self.field.info['disc'] in ['GSSNE', 'GAUSS'])\
                and group_filter:
            extract = result.mesh_source()
            pvs.SetActiveSource(extract)
            extract.FieldsStatus = [result.mesh]
            extract = BaseRep.register_source('ExtractGroup', extract,
                                              label='<GROUP EXTRACTION FROM MESH>')
            pvs.SetActiveSource(extract)
            extract.AllGroups = ['GRP_{}'.format(gr) for gr in group_filter]
            extract.UpdatePipeline()

            pvs.SetActiveSource(new_source)
            new_source = BaseRep.register_source('ResampleWithDataset', '_',
                                                 SourceDataArrays=new_source,
                                                 DestinationMesh=extract,
                                                 label='<GROUP FILTER>')
            new_source.MarkBlankPointsAndCells = True
            new_source.UpdatePipeline()

            if self.field.info['disc'] in ('GAUSS',):
                pvs.SetActiveSource(new_source)
                new_source = BaseRep.register_source(
                    'PointDatatoCellData', new_source, label='<{}> BACK TO CELL DATA'.format(
                        osp.basename(self.field.concept.result.path)))
                new_source.UpdatePipeline()

        if new_source:
            new_source.UpdatePipeline()
            new_source.UpdatePipelineInformation()
            # pvs.Hide(self.source, self.ren_view)
            pvs.SetActiveSource(new_source)
            self.source = new_source

        if colcomp == 'Magnitude':
            # # The following step is necessary in order to force
            # # the application of the filter for _EL* fields
            # if new_source and '_EL' in self.field.name:
            #     pvs.Show(new_source, self.ren_view)
            #     new_source = None

            mag_comps = []
            if self.field.name in VECTOR_READY_FIELDS:
                mag_comps = TRANSLATIONAL_COMPS
                arrname = '{}:MAGTRAN'.format(self.array)
                label = '<{}:{}> (TRANSLATION MAG.)'.format(
                    self.field.concept.name, self.field.name)
                att_type = 'Point Data' \
                    if self.field.info['support']=='POINTS' \
                    else 'Cell Data'
            # elif self.field.name in FIELDS_WITH_MAG:
            #     mag_comps = ['SIXX', 'SIYY', 'SIZZ']
            #     arrname = '{}:MAGSTRESS'.format(self.array)
            #     label = '<{}:{}> PRINCIPAL STRESSES MAG.'.format(
            #         self.field.concept.name, self.field.name)
            #     pvs.Hide(new_source, self.ren_view)
            #     att_type = 'Cell Data' if '_ELGA' in self.field.name else 'Point Data'
            if mag_comps:
                array = self.field.info['pv-aident']
                formula = []
                for comp in mag_comps:
                    if comp in self.field.info['components']:
                        formula.append('"{}_{}"^2'.format(array, comp))
                formula = '+'.join(formula)
                formula = str('sqrt({})').format(formula)

                new_source = BaseRep.register_source(
                    'Calculator', self.source, ResultArrayName=str(arrname),
                    Function=str(formula), AttributeType=str(att_type),
                    label=str(label))
                self.array = arrname
                pvs.Show(new_source, self.ren_view)

            if new_source:
                pvs.SetActiveSource(new_source)
                self.source = new_source

        # Save the base source for later use, for example
        # if the user changes the slice properties
        self.base_source = self.source
        self.update_slice()

    def update_slice(self):
        """
        Creates and updates slice information as needed
        """
        if 'Slice' not in self.opts:
            return

        import pvsimple as pvs

        slice_active = (self.opts['Slice'] != 'None')
        if slice_active:
            slice_normal = {'Normal to x-axis': [1., 0., 0.],
                            'Normal to y-axis': [0., 1., 0.],
                            'Normal to z-axis': [0., 0., 1.]}[self.opts['Slice']]

            data_info = self.base_source.GetDataInformation().DataInformation
            bounds = data_info.GetBounds()
            bounds_indices = {'Normal to x-axis': [0, 1, 0],
                              'Normal to y-axis': [2, 3, 1],
                              'Normal to z-axis': [4, 5, 2]}[self.opts['Slice']]
            ind = bounds_indices[-1]
            box_min, box_max = [bounds[i] for i in bounds_indices[:-1]]

            slice_pos = box_min + \
                self.opts['SlicePosition'] * (box_max - box_min)

            slice_orig = [bounds[1] - bounds[0],
                          bounds[3] - bounds[2],
                          bounds[5] - bounds[4]]
            slice_orig[ind] = slice_pos


            label = '<CLIP> {}'.format(self.opts['Slice'])
            self.source = BaseRep.register_source('Clip',
                                                  self.base_source, label=label)
            self.source.ClipType.Origin = slice_orig
            self.source.ClipType.Normal = slice_normal

            pvs.SetActiveSource(self.source)
            pvs.Hide3DWidgets(proxy=self.source.ClipType)

            # BaseRep.show_reference(self)
        else:
            # Slice option set to None
            self.source = self.base_source
            pvs.SetActiveSource(self.source)
            self.hide_reference()

    def update_colorbar(self, timechange=False, pvsup=None):
        """
        Adds (or updates an existing) for the current representation

        'timechange' flag allows to handle the cases where the colorbar
        needs to be updated due to a change in time (using pvcontrols)

        For example the rescale to all steps needs not to be updated
        in this case, which allows to optimize the calculation times.
        """
        import pvsimple as pvs
        from ..utils import (colorbar_title)

        display = self.display

        pvsup = str(self.field.info['support']) if pvsup is None else pvsup
        colbasis = str(self.array)
        colcomp = str(self.opts['Component']
                      if 'Component' in self.opts else 'Magnitude')

        display.SelectInputVectors = [pvsup, colbasis]

        if colcomp in ['Scalar']:
            pvs.ColorBy(display, (pvsup, colbasis))
        else:
            pvs.ColorBy(display, (pvsup, colbasis, colcomp))

        if 'Title' not in self.opts:
            self.opts['Title'] = colorbar_title(self.field.info['label'], colcomp)

        conti = (self.opts['ColorBarType'] == 'Continuous')
        if conti:
            auto_color_mode = self.opts['ColorBarAuto']\
                if 'ColorBarAuto' in self.opts\
                else ['Automatic: current step']
            auto_color = ('Automatic' in auto_color_mode)
            if auto_color:
                # Insure that the pipeline is updated...
                self.source.UpdatePipeline()
                all_steps = 'all steps' in auto_color_mode
                if all_steps:
                    if not timechange:
                        vmin, vmax = get_full_array_range(
                            self.source, colbasis, colcomp, atype=pvsup.lower()[:-1])
                    else:
                        vmin, vmax = self.opts[
                            'ColorBarMin'], self.opts['ColorBarMax']
                    self.opts['ColorBarAuto'] = 'Automatic: all steps'
                else:
                    # display.RescaleTransferFunctionToDataRange(True, False)
                    vmin, vmax = get_array_range(
                        self.source, colbasis, colcomp, atype=pvsup.lower()[:-1])
                    self.opts['ColorBarAuto'] = 'Automatic: current step'

                # Save the min and max values which will be enforced later
                # on...
                self.opts['ColorBarMin'], self.opts['ColorBarMax'] = vmin, vmax
                if not self.opts['ColorBarCategorical']:
                    self.opts['ColorBarCategorical'] = {
                        'RGBPoints': [vmin, 0.0, 0.0, 1.0,
                                      0.5 * (vmin + vmax) -
                                      1e-8, 0.0, 0.0, 1.0,
                                      0.5 * (vmin + vmax), 1.0, 0.0, 0.0,
                                      vmax, 1.0, 0.0, 0.0],
                        'Annotations': ['', 'Range 1', '', 'Range 2']}
        else:
            color_array = self.opts['ColorBarCategorical']

        display.SetScalarBarVisibility(self.ren_view, True)

        coltf = pvs.GetColorTransferFunction(colbasis)
        if conti:
            coltf.RescaleTransferFunction(self.opts['ColorBarMin'],
                                          self.opts['ColorBarMax'])
            coltf.ApplyPreset('Rainbow Uniform', True)
            coltf.Annotations = []
        else:
            coltf.RGBPoints = color_array['RGBPoints']
            coltf.Annotations = color_array['Annotations']

        coltf_cbar = pvs.GetScalarBar(coltf, self.ren_view)

        coltf_cbar.Title = self.opts['Title']
        coltf_cbar.TitleColor = [0.0, 0.0, 0.0]
        coltf_cbar.LabelColor = [0.0, 0.0, 0.0]
        coltf_cbar.TextPosition = str(
            'Ticks left/bottom, annotations right/top')

        coltf_cbar.Orientation = str('Vertical')
        coltf_cbar.WindowLocation = str('Any Location')
        coltf_cbar.Position = [0.97, 0.20] if conti else [0.90, 0.20]
        coltf_cbar.ScalarBarLength = 0.40
        coltf_cbar.ScalarBarThickness = 16

        coltf_cbar.ComponentTitle = ''
        if 'Unit' in self.opts:
            if self.opts['Unit']:
                coltf_cbar.ComponentTitle = '[{}]'.format(self.opts['Unit'])
        else:
            self.opts['Unit'] = ''

        pvs.HideUnusedScalarBars()
        return coltf_cbar
