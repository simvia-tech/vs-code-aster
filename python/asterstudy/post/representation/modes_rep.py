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
ModesRep: modes representation and animation for displacement vector fields
"""

import os.path as osp

from ..config import TRANSLATIONAL_COMPS
from ..utils import dbg_print, default_scale, nb_points_cells
from .base_rep import BaseRep
from .color_rep import ColorRep


class ModesRep(ColorRep):
    """ModesRep implementation."""

    name = 'Mode Animation'

    pickable = False
    mod_source = None

    def defaults(self):
        """
        Add default options to self.opts, called after initialization
        and prior to the represent function
        """
        ColorRep.defaults(self)

        if 'ScaleFactorAuto' in self.opts:
            scale_auto = self.opts['ScaleFactorAuto']
        else:
            scale_auto = 'ScaleFactor' not in self.opts
            if 'ScaleFactor' in self.opts:
                scale_auto = (self.opts['ScaleFactor'] < 1.e-18)

        if scale_auto:
            self.opts['ScaleFactorAuto'] = True
            self.opts['ScaleFactor'] = default_scale(
                self.field.concept.result.source,
                self.field.info['pv-aident'])
        else:
            self.opts['ScaleFactorAuto'] = False

        self.opts.pop('Slice', None)
        self.opts.pop('SlicePosition', None)
        self.opt_groups['Representation'] = [
            'Component', 'ScaleFactorAuto', 'ScaleFactor']

        if 'NbPeriods' not in self.opts:
            self.opts['NbPeriods'] = 2

        self.opts['FrameRate'] = 30

        self.opt_groups.update({'Animation': ['NbPeriods', 'FrameRate']})
        self.opt_groups['Color bar'].remove('Title')
        self.opt_groups['Color bar'].remove('Unit')

    def customize_source(self):
        """
        Overload the default source by using a Glyph filter
        to calculate a translational vector of nodal forces
        or reaction forces.
        """
        import pvsimple as pvs

        result = self.field.concept.result
        self.mod_source = result.source_as_mode()
        self.mod_source.FieldsStatus = [self.field.info['pv-key']]
        self.mod_source.UpdatePipeline()

        self.source = self.mod_source
        if result.quadratic:
            linearized = BaseRep.register_source('QuadraticToLinear',
                                                  self.source, label='<{}> QUAD. TO LINEAR'.format(
                                                      osp.basename(self.field.concept.result.path)))
            linearized.UpdatePipeline()
            if nb_points_cells(linearized)[0] > 0:
                self.source = linearized
            else:
                result.quadratic = False

        group_filter = []
        if self.opts['GroupsFilter']:
            group_filter = [gr[0] for gr in self.opts['GroupsFilterOptions']
                            if gr[1]]
        if group_filter:
            extract = result.mesh_source()
            pvs.SetActiveSource(extract)
            extract.FieldsStatus = [result.mesh]
            extract = BaseRep.register_source('ExtractGroup', extract,
                                              label='<GROUP EXTRACTION FROM MESH>')
            pvs.SetActiveSource(extract)
            extract.AllGroups = ['GRP_{}'.format(gr) for gr in group_filter]
            extract.UpdatePipeline()

            pvs.SetActiveSource(self.source)
            self.source = BaseRep.register_source('ResampleWithDataset', '_',
                                                  SourceDataArrays=self.source,
                                                  DestinationMesh=extract,
                                                  label='<GROUP FILTER>')
            self.source.MarkBlankPointsAndCells = True
            self.source.UpdatePipeline()

        # Note that the scale factor is intentially not registered
        # so as to avoid new warps are created each time the scale is
        # changed by the user !
        self.source = BaseRep.register_source('WarpByVector', self.source,
                                              label='<{}:{}> MODES ANIMATION'.format(
                                                  self.field.concept.name, self.field.name))

        # self.source = BaseRep.register_source('Normalmodesanimationreal',
        #     self.mod_source, label='<{}:{}> MODES ANIMATION'.format(
        #         self.field.concept.name, self.field.name))

        # self.array = '__NormalModesAnimation__' #The name of the variable
        # scaling
        self.update_modes()

        # Create animation and play it once
        self.animate(play=False)

    def update(self, mod_opts):
        """
        Update the warped field representation based on changes
        in scale factor, in representation, or colored component
        """
        ColorRep.update(self, mod_opts)

        if 'ScaleFactorAuto' in mod_opts or 'ScaleFactor' in mod_opts:
            if self.opts['ScaleFactorAuto']:
                self.opts['ScaleFactor'] = default_scale(
                    self.field.concept.result.source,
                    self.field.info['pv-aident'])
        self.update_modes()

    def update_display_props(self, mod_opts):
        """
        Shortcut to calling the animate method each time
        the user clicks of animate mode
        """
        BaseRep.update_display_props(self, mod_opts)

        # This forces the timeline for the animation to be recalculated
        if 'NbPeriods' in mod_opts:
            self.scene = None

    def update_source(self, mod_opts):
        """
        Overload ColorRep update_source method so that no
        change in source is done upon updating the representation
        (change in components or scale factor).

        Note update_source is called from ColorRep.update(..)

        self.source thus does not change and refers to the
        Warp filter output
        """

    def update_modes(self):
        """
        Updates glyphs by changing the scale of the representation
        """
        import re
        import pvsimple as pvs

        # Search for the array name corresponding to the selected mode
        mode_ind = 0
        mode_freq = self.ren_view.ViewTime
        timesteps = list(self.field.concept.result.full_source.TimestepValues)
        if mode_freq in timesteps:
            mode_ind = timesteps.index(mode_freq)
        else:
            dbg_print(
                'Error finding frequency {} Hz, selecting first mode'.format(mode_freq))

        arrname = ''
        nbarr = self.mod_source.PointData.NumberOfArrays
        look = re.compile(
            r"{} \[0*{}\]\s".format(self.field.info['pv-aident'], mode_ind))
        for i in range(nbarr):
            arrname = self.mod_source.PointData.GetArray(i).Name
            if look.match(arrname):
                if len(self.field.info['components']) > 3:
                    if self.opts[
                            'Component'] in TRANSLATIONAL_COMPS + ['Magnitude']:
                        if 'Vector' in arrname:
                            break
                    else:
                        break
                else:
                    break

        if not arrname:
            dbg_print(
                'Error encountered finding the array name for the mode animation')

        self.array = arrname
        self.source.Vectors = [None, arrname]
        self.source.ScaleFactor = self.opts['ScaleFactor']

        # self.source.ModeArraySelection = ['POINTS', arrname]
        self.source.UpdatePipeline()
        pvs.SetActiveSource(self.source)
        pvs.Show(self.source)

        # Add mode identifier annotation text
        text_str = str('Mode {}: {:g} Hz'.format(mode_ind + 1, mode_freq))

        text = BaseRep.register_source('Text', 'root',
                                       Text='Modes', label='<MODE IDENTIFIER>')

        text.Text = text_str
        display = pvs.Show(text, self.ren_view)

        display.FontFamily = str('Arial')
        display.FontSize = 15
        display.Color = (0.25, 0.25, 0.45)
        display.WindowLocation = str('Any Location')
        display.Position = [0.80, 0.95]

        self.ren_view.Update()

        # Show reference position in transparent mode
        BaseRep.show_reference(self)

    def animate(self, play=True):
        """
        Animates the current mode
        """
        import pvsimple as pvs

        # Either use the PV (global) scene or create a new
        # Animation scene instance
        glob = True

        # Acquire an animation scene
        if glob:
            self.scene = pvs.GetAnimationScene()
        else:
            self.scene = pvs.servermanager.animation.AnimationScene()
        self.scene.ViewModules = [self.ren_view]

        # Create a cue to animate the AnimationTime property
        if glob:
            cue = pvs.GetAnimationTrack('ScaleFactor', index=0,
                                        proxy=self.source)
        else:
            cue = pvs.servermanager.animation.KeyFrameAnimationCue()
            cue.AnimatedProxy = self.source
            cue.AnimatedPropertyName = 'ScaleFactor'

        # Create keyframes for this animation track
        kfs = []
        nb_periods = self.opts['NbPeriods']
        # for i in range(nb_periods+1):
        #     kfs.append(pvs.CompositeKeyFrame())
        #     kfs[-1].KeyTime = float(i)/nb_periods
        #     kfs[-1].KeyValues = [self.opts['ScaleFactor']]
        #     kfs[-1].Interpolation = 'Sinusoid'

        for i in range(2 * nb_periods + 1):
            kfs.append(pvs.CompositeKeyFrame())
            kfs[-1].KeyTime = (0.5 * i) / (nb_periods)
            kfs[-1].KeyValues = [(-2. * (i % 2) + 1) *
                                 self.opts['ScaleFactor']]
            kfs[-1].Interpolation = 'Ramp'

        cue.KeyFrames = kfs
        cue.Enabled = 1

        self.scene.Cues = [cue]

        self.scene.StartTime = 0
        self.scene.EndTime = 1
        self.scene.PlayMode = 'Real Time'
        # self.scene.PlayMode = 'Snap To TimeSteps'
        self.scene.Duration = nb_periods
        self.scene.Loop = 0

        if play:
            self.scene.Play()

    def update_colorbar(self, timechange=False, pvsup=None):
        """
        Do the coloring but hide the bar for modal representation !
        """
        ColorRep.update_colorbar(self, timechange)

        # Do not propose title and unit for modal representation
        self.opts.pop('Title', None)
        self.opts.pop('Unit', None)
        self.display.SetScalarBarVisibility(self.ren_view, False)
