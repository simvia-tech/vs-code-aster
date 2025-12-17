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
Post-processing
---------------

The module implements the classes required for parsing and manipulating
results in the Results tab of AsterStudy GUI.

"""

from .config import GROUPS_FILTER_LIMIT, TRANSLATIONAL_COMPS
from .utils import is_quadratic, mesh_dims_nbno, parse_file


class ResultFile():
    """ResultFile implementation."""

    full_source = source = extract_source = dup_source = mode_source = None
    filter_source = group_filter = concepts = quadratic = None
    mesh_proxy = temp_mesh = None

    def __init__(self, path):
        """
        Parse a new result file given its filename

        Arguments:
            path (str): full path of the result file to post-process
                        (MED format)
        """
        import pvsimple as pvs
        import os.path as osp
        self.full_source = pvs.MEDReader(FileNames=[path])
        pvs.RenameSource('<{}> LOADED'.format(osp.basename(path)),
                         self.full_source)
        # self.source contains several interesting references/infos
        # >> steps : self.source.AllTimeSteps.Available, array of strings
        #            self.source.TimestepValues for numeric values !
        # >> file_name : self.source.FileNames[0]

        # Parse information from the result file and determine the concept names
        # as well as the field informations
        finfos = parse_file(self.full_source)
        # print(("Parsing result {}".format(path)))
        # for cname in finfos:
        #     print("  >>", cname, finfos[cname])

        self.concepts = [None] * len(list(finfos.keys()))
        for i, cname in enumerate(finfos.keys()):
            self.concepts[i] = ResultConcept(self, cname, finfos[cname])

        self.dims_nbno, self.temp_mesh = mesh_dims_nbno(path)

        # This flag is set to None if there are no QUAD9 elems
        # It is set by default to 0 if QUAD9 elems are detected
        # ------------------------------------------------------------
        # It can be changed by the user (to 1) as to activate special
        # treatments in the representations for 3d shells supported by
        # such (QUAD9) elems, in particular applying QuadraticToLinear
        # Paraview filters
        self.quadratic = is_quadratic(self.dims_nbno)

        self.parse_mesh_groups()

        self.source = self.full_source
        # print('Done initializing ResultFile')


    def is_empty(self):
        """
        Returns whether the result file contains fields that can be
        visualized or not...
        """
        if not self.concepts:
            return True

        for concept in self.concepts:
            if concept.fields:
                return False

        return True

    @property
    def path(self):
        """
        Full result file path
        """
        return self.full_source.FileNames[0]

    @property
    def max_dim(self):
        """
        Maximum mesh dimension (0 -> 3)
        """
        return max([x[0] for x in self.dims_nbno])

    def lookup(self, cname):
        """
        Looks up a concept given its name
        """
        for concept in self.concepts:
            if concept.name == cname:
                return concept
        return None

    def duplicate_source(self):
        """
        Duplicates the source if needed by reading the mesh file again
        """
        import pvsimple as pvs
        import os.path as osp
        if not self.dup_source:
            self.dup_source = pvs.MEDReader(FileNames=[self.path])
            pvs.RenameSource(
                '<{}> DUPLICATED'.format(
                    osp.basename(
                        self.path)),
                self.dup_source)
        return self.dup_source

    def mesh_source(self):
        """
        Load the temporary mesh
        """
        import pvsimple as pvs
        import os.path as osp
        if not self.mesh_proxy:
            self.mesh_proxy = pvs.MEDReader(FileNames=[str(self.temp_mesh)])
            pvs.RenameSource(
                '<{}> MESH SOURCE'.format(
                    osp.basename(
                        self.path)),
                self.dup_source)
        return self.mesh_proxy

    def source_as_mode(self):
        """
        Loads the main result file in Mode format
        """
        import pvsimple as pvs
        import os.path as osp
        if not self.mode_source:
            self.mode_source = pvs.MEDReader(FileNames=[self.path],
                                             TimeModeProperty=1,
                                             VectorsProperty=1)
            pvs.RenameSource(
                '<{}> AS MODE'.format(
                    osp.basename(
                        self.path)),
                self.mode_source)

        return self.mode_source

    def toggle_quadratic(self):
        """
        Toggles the self.quadratic flag upon user choice
        """
        if self.quadratic is not None:
            self.quadratic = 0 if self.quadratic == 1 else 1

    def parse_mesh_groups(self):
        """
        Parses available mesh groups from the input (MED) file
        """
        self.groups = [['Mesh information not available', False]]
        self.group_filter = []

        if hasattr(self, 'mesh'):
            import pvsimple as pvs
            # Retrieve the list of available mesh groups and their types
            mesh_source = self.mesh_source()
            keys = mesh_source.GetProperty("FieldsTreeInfo")[::2]
            self.mesh = keys[0]
            mesh_source.FieldsStatus = [self.mesh]

            extract = pvs.ExtractGroup(Input=mesh_source)
            # brut_groups contains groups and families, this needs to be
            # parsed further.
            # Note: the use of extract.AllGroups would only work in GUI mode
            # and thus breaks all unit tests
            brut_groups = extract.GetProperty("GroupsFlagsInfo")[::2]
            pvs.Delete(extract)

            if len(brut_groups) > GROUPS_FILTER_LIMIT:
                return

            sep = mesh_source.GetProperty('Separator').GetData()

            # These are the actual group names, we still need to determine
            # their types by reading the family information
            names = [gr[4:] for gr in brut_groups if gr[:4] == 'GRP_']
            self.groups = []
            for grname in names:
                supp = None
                for grfam in brut_groups:
                    if not grfam[:4] == 'FAM_':
                        continue
                    if grname in grfam:
                        supp = grfam.split(sep)[-1]
                        break
                if supp:
                    self.groups.append([grname, supp])

    def filter_groups_legacy(self, group_filter, input_source=None):
        """
        **Legacy** method for reading and filtering results on certain groups
        group_filter is a list of groups that is handled from the underlying
        representation.

        This method is generally robust but can be time consuming and may
        give imprecise results for element fields because data resampling is
        applied.

        A more direct approach in the method filter_groups was introduced
        starting SM2023.
        """
        if self.group_filter == group_filter:
            return self.filter_source

        import pvsimple as pvs
        if not group_filter or 'not available' in group_filter[0]:
            self.source = self.full_source
            pvs.SetActiveSource(self.source)
            self.group_filter = []
            return self.full_source

        # This allows applying filter on the mode source for example
        source = input_source if input_source else self.full_source

        mesh_source = self.mesh_source()
        mesh_source.FieldsStatus = [self.mesh]
        if not self.extract_source:
            self.extract_source = pvs.ExtractGroup(mesh_source)
            pvs.RenameSource(
                '<GROUP EXTRACTION FROM MESH>',
                self.extract_source)

        pvs.SetActiveSource(self.extract_source)
        self.extract_source.AllGroups = \
            ['GRP_{}'.format(gr) for gr in group_filter]

        if not self.filter_source:
            self.filter_source = pvs.ResampleWithDataset()
            self.filter_source.MarkBlankPointsAndCells = True
            self.filter_source.ComputeTolerance = True
            self.filter_source.CellLocator = str('Cell Locator')
            self.filter_source.PassCellArrays = True
            self.filter_source.PassPointArrays = True

        pvs.SetActiveSource(source)
        self.filter_source.SourceDataArrays = source
        self.filter_source.DestinationMesh = self.extract_source

        self.filter_source.UpdatePipeline()
        self.filter_source.UpdatePipelineInformation()
        pvs.RenameSource('<RESAMPLING ON GROUP>', self.filter_source)
        pvs.Render()

        if not input_source:
            self.source = self.filter_source

        self.group_filter = group_filter
        return self.filter_source


    def filter_groups(self, group_filter, input_source=None):
        """
        Reads and filters the results source on the requested groups
        group_filter is a list of groups that is handled from the underlying
        representation.
        """
        from .representation import BaseRep

        if self.group_filter == group_filter:
            return self.extract_source

        import pvsimple as pvs
        if not group_filter or 'not available' in group_filter[0]:
            self.source = self.full_source
            pvs.SetActiveSource(self.source)
            self.group_filter = []
            return self.full_source

        # This allows applying filter on the mode source for example
        source = input_source if input_source else self.full_source

        # Add (or reuse) a group extraction filter
        self.extract_source = BaseRep.register_source(
            'ExtractGroup', source, label='<GROUP EXTRACTION >')

        pvs.SetActiveSource(self.extract_source)
        self.extract_source.AllGroups = [f'GRP_{gr}' for gr in group_filter]
        pvs.Render()

        if not input_source:
            self.source = self.extract_source

        self.group_filter = group_filter
        return self.extract_source

class ResultConcept():
    """ResultConcept implementation."""

    result = name = fields = None

    def __init__(self, result, name, finfos):
        """
        Create/intialize a new concept based on preliminary
        parsed fields information.

        Arguments:
            result (ResultFile): parent result file.
            name (str): concept name.
            finfos (dict): parsed fields information.
        """
        # print("Initializing concept {}".format(name))
        self.result = result
        self.name = name

        self.fields = []
        for fname in finfos:
            # Do not associate the mesh fields to a concept
            if finfos[fname]['mesh'] == fname:
                self.result.mesh = finfos[fname]['pv-key']
                continue
            field = ConceptField(self, fname, finfos[fname])
            self.fields.append(field)

        # print('Done initializing ResultConcept')

    def lookup(self, fname):
        """
        Looks up a field given its name
        """
        for field in self.fields:
            if field.name == fname:
                return field
        return None


class ConceptField():
    """ConceptField implementation."""

    concept = name = info = None
    params = {}

    def __init__(self, concept, name, info):
        """
        Create a new field based on preliminary parsed
        information from a concept read in a results file.

        Arguments:
            result (ResultConcept): parent concept.
            info (dict): userful information about the field

        ***************
        <info> contents
        ***************
        label: field label created based on the aster field name
        pv-key: paraview field identifier key <--- useful to filter out other fields
        pv-aident: paraview array identifier <--- useful in selection/coloring/etc.
        pv-fident: key identifiers for fields from the same series
        components: available components within the field
        support: geometrical support (point or cell)

        """
        # print("Initializing field {}".format(name))
        self.concept = concept
        self.name = name
        self.info = info
        # print('Done initializing ConceptField')

    def needs_extraction(self):
        """
        Method that verifies whether tranlsational extraction of
        the field is required (Displacement or force fields)
        """
        comps = self.info['components']
        if len(comps) != 3:
            return True

        for comp in comps:
            if comp not in TRANSLATIONAL_COMPS:
                return True

        if self.info.get('support', 'POINTS') == 'CELLS':
            return True

        return False
