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

"""
VectorRep: vector (arrow glyphs) representation of vector (point) fields
"""

from ..config import TRANSLATIONAL_COMPS
from ..utils import get_array_range
from .base_rep import BaseRep
from .color_rep import ColorRep


class VectorRep(ColorRep):
    """VectorRep (Glyphs) implementation."""

    name = 'Vector Representation (Glyphs)'
    pickable = False  # Probing and plotting are not allowed
    glyph_array = None

    def defaults(self):
        """
        Add default options to self.opts, called after initialization
        and prior to the represent function
        """
        ColorRep.defaults(self)

        if 'MaxArrowSize' not in self.opts:
            data_info = self.source.GetDataInformation().DataInformation
            xmin, xmax, ymin, ymax, zmin, zmax = data_info.GetBounds()
            box_dim_max = max([xmax - xmin, ymax - ymin, zmax - zmin])
            self.opts['MaxArrowSize'] = box_dim_max * 0.05

        self.opts.pop('Slice', None)
        self.opts.pop('SlicePosition', None)
        self.opt_groups['Representation'] = ['Component', 'MaxArrowSize']

    def customize_source(self): # pragma pylint: disable=duplicate-code
        """
        Overload the default source by using a Glyph filter
        to calculate a translational vector of nodal forces
        or reaction forces.
        """
        import pvsimple as pvs

        ColorRep.customize_source(self)
        pvs.Hide(self.source, self.ren_view)

        if self.field.needs_extraction():
            point_source = self.source

            array = self.field.info['pv-aident']
            comps = [c for c in self.field.info['components'] if c in TRANSLATIONAL_COMPS]
            arrname = '{}:TRAN'.format(array)
            trans = BaseRep.register_source('ExtractComponents',
                                            point_source, InputArray=['POINTS', array],
                                            OutputArrayName=arrname,
                                            label='<{}:{}> (TRANSLATION)'.format(
                                                self.field.concept.name, self.field.name))

            trans.UpdatePipeline()
            trans.Components = comps
            trans.GenerateVector = 1

            trans.UpdatePipeline()
            trans.UpdatePipelineInformation()


            self.glyph_array = str(arrname)
        else:
            trans = self.source
            self.glyph_array = self.field.info['pv-aident']

        pvs.SetActiveSource(trans)
        self.source = BaseRep.register_source('Glyph', trans,
                                              GlyphType='Arrow', GlyphMode='All Points',
                                              label='<{}:{}> VECTOR REP (GLYPHS)'.format(
                                                  self.field.concept.name, self.field.name))

        self.source.GlyphType.TipResolution = 20
        self.source.GlyphType.ShaftResolution = 20

        # Force selection of the proper coloring array
        self.update_source({'Component': ''})
        self.update_glyphs()

    def update(self, mod_opts):
        """
        Update the warped field representation based on changes
        in scale factor, in representation, or colored component
        """
        ColorRep.update(self, mod_opts)

        if 'MaxArrowSize' in mod_opts:
            self.update_glyphs()

    def update_source(self, mod_opts):
        """
        For the vector representation the array name for coloring may
        need to be adjusted as to treat magnitude and rotational
        coloring for displacement or forces with structural elements.

        Note update_source is called from ColorRep.update(..)

        self.array is used in order to color the glyph representation.
        """
        if 'Component' in mod_opts:
            array = self.field.info['pv-aident']
            self.array = array
            if (self.opts['Component'] == 'Magnitude'
                    and len(self.field.info['components']) > 3):
                # Note that this is calculated by ColorRep
                self.array = '{}:MAGTRAN'.format(array)

    def update_glyphs(self):
        """
        Updates glyphs by changing the scale of the representation
        """
        self.source.OrientationArray = ['POINTS', self.glyph_array]
        self.source.ScaleArray = ['POINTS', self.glyph_array]
        self.source.VectorScaleMode = 'Scale by Magnitude'

        # MaximumGlyphSize --- Depreciated in Paraview 5.7
        # self.source.MaximumGlyphSize = self.opts['MaxArrowSize']
        _, vmax = get_array_range(self.source, self.array, 'Magnitude')
        if abs(vmax) > 1.e-8:
            self.source.ScaleFactor = self.opts['MaxArrowSize']/vmax
        else:
            self.source.ScaleFactor = 1.0

        self.source.UpdatePipeline()

        BaseRep.show_reference(self)
