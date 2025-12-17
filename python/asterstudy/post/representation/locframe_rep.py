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
LocalFrameRep: vector (arrow glyphs) representation for local frames
"""

from .base_rep import DISPLAY_PROPS_DEFAULTS, BaseRep
from .vector_rep import VectorRep


class LocalFrameRep(BaseRep):
    """LocalFrameRep (Glyphs) implementation."""

    name = 'Local Frame Representation (Glyphs)'
    axes_reps = None

    def defaults(self):
        """
        Add default options to self.opts, called after initialization
        and prior to the represent function
        """
        BaseRep.defaults(self)

        if 'ScaleFactor' not in self.opts:
            data_info = self.source.GetDataInformation().DataInformation
            xmin, xmax, ymin, ymax, zmin, zmax = data_info.GetBounds()
            box_dim_max = max([xmax - xmin, ymax - ymin, zmax - zmin])
            self.opts['ScaleFactor'] = box_dim_max * 0.02

        self.opt_groups['Color bar'] = {}
        self.opt_groups['Representation'] = ['ScaleFactor']

    def represent(self): # pragma pylint: disable=duplicate-code
        """Update the representation
        """
        import pvsimple as pvs
        colors = ([1.0, 0., 0.], [0., 1., 0.], [0., 0., 1.])

        self.axes_reps = []
        fnames = ['_X', '_Y', '_Z']
        if self.field.name.startswith('.REPLO'):
            fnames = ['.REPLO_{}'.format(i+1) for i in range(3)]

        for i, fname in enumerate(fnames):
            field = self.field.concept.lookup(fname)
            if field is None:
                continue

            axrep = VectorRep(field)
            pvs.ColorBy(axrep.display, None)
            axrep.display.AmbientColor = colors[i]
            axrep.display.DiffuseColor = colors[i]
            axrep.display.Ambient = 0.15
            axrep.display.Representation = 'Surface'
            axrep.display.SetScalarBarVisibility(self.ren_view, False)

            self.axes_reps.append(axrep)
        self.update(self.opts)

    def update(self, mod_opts):
        """
        Update the warped field representation based on changes
        in scale factor, in representation, or colored component
        """
        import pvsimple as pvs

        for _, axrep in enumerate(self.axes_reps):
            axrep.source.ScaleFactor = self.opts['ScaleFactor']
            axrep.source.UpdatePipeline()

        BaseRep.show_reference(self)
        pvs.HideUnusedScalarBars()

        self.opt_groups['Color bar'] = {}

    def update_display_props(self, mod_opts):
        """
        Updates display properties (Representation and Opacity)
        """
        for mod_opt in mod_opts:
            if mod_opt in DISPLAY_PROPS_DEFAULTS[0]:
                for rep in self.axes_reps:
                    setattr(rep.display, mod_opt, self.opts[mod_opt])
