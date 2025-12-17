# -*- coding: utf-8 -*-

# Copyright 2016 EDF R&D
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
Case
----

Implementation of the study case.

"""


import itertools
import os
import os.path as osp
from collections import OrderedDict

from ..common import (debug_message, info_message, is_subpath,
                      no_new_attributes, same_path)
from .abstract_data_model import Node, add_parent, remove_parent
from .command import Variable
from .dataset import DataSet
from .general import ConversionLevel
from .general import CopyContext as Ctx
from .general import FileAttr, Validity
from .job_informations import JobInfos
from .result import CaseMixing as RCaseMixing
from .sd_dict import SD_DICT
from .stage import Stage


class Case(Node, RCaseMixing):
    """
    Study case.

    Case consists of Stages each of which, in its turn, represents
    separate code_aster COMM file.

    New empty Stage can be added to the Case by `create_stage()`
    method. Similarly, `import_stage()` method allows importing
    existing code_aster COMM file to the Case as a new Stage.
    """

    basicNaming = 0
    autoNaming = 1
    naming_system = autoNaming

    _generated_names = None
    _in_dir = _out_dir = _job_infos = None
    __setattr__ = no_new_attributes(object.__setattr__)

    def __init__(self, name):
        """
        Create Case.

        Arguments:
            name (str): Name of the Case.
        """
        Node.__init__(self, name)
        RCaseMixing.__init__(self)
        self.shallow_copy = Stage
        self._generated_names = set()
        self._in_dir = self._out_dir = None
        self._job_infos = JobInfos(with_default=True)
        if os.getenv("ASTERSTUDY_NAMING", None) == "basic":
            self.use_basic_naming()

    def __mul__(self, other):
        """Support native Python '*' operator protocol."""
        Node.__mul__(self, other)

        RCaseMixing.__mul__(self, other)

    def copy(self, name=None):
        """
        Create a copy of this Case.

        Arguments:
            name (Optional[str]): Name for copied Case. Defaults to
                *None* (name is automatically generated).

        Returns:
            Case: A copy of this Case.
        """
        return self.model.copy(self, name=name)

    def initialize_copy(self):
        """
        Hook function: called when this Case is copied.

        Bare copy: Create new empty Case.

        Returns:
            Case: New empty Case.
        """
        return Case(self.name)

    def customize_copy(self, orig, **kwargs):
        """
        Hook function: attune data model additionally after a Case
        has been copied.

        This method is called for the Case which has been just created
        via `copy()` method, i.e. for the copy of original Case.

        As result new Case is added to the History:

        - Previous Current Case is moved to the list of Run Cases;
        - New Case becomes the Current Case.

        See `History.add_case()` for more details.

        Arguments:
            orig (Case): Original Case object freshly replicated.
            name (Optional[str]): Name for copied Case. Defaults to
                *None*.
        """
        name = kwargs.get('name')
        if name is not None:
            self.name = name
        self._in_dir = orig.in_dir
        self._out_dir = orig.out_dir
        self._job_infos = orig.job_infos.copy()

        # The new case is not inserted last but second to last
        #     so that the instance that is tagged as `current`
        #     is not changed by a copy operation.
        self.model.insert_case(self, index=-1)

    def rename(self, name):
        """
        Renames the case.

        Arguments:
            name (str): New name.
        """
        self.name = name
        self.rename_folder()

    def name_exists(self, name):
        """Tell if `name` is an existing Case name.

        Arguments:
            name (str): Proposed name.

        Returns:
            bool: *True* if another Case with this name already exists.
        """
        return name in [i.name for i in self.model.cases
                        if i is not self]

    def __contains__(self, given):
        """
        Support native Python "in" operator protocol.

        Arguments:
            given (Stage or str): Stage being checked.

        Returns:
            bool: *True* if Stage is contained in the Stage; *False*
            otherwise.
        """
        if isinstance(given, Stage):
            return next((True for item in self if item is given), False)

        return next((True for item in self if item.name == given), False)

    def __getitem__(self, given):
        """
        Support native Python '[]' operator protocol.

        Arguments:
            given (int, slice, str): Reference argument for operator:

                - int: to access child Stage by index
                - slice: to access range of Stages by slice expression (start
                    index is always 0)
                - str: to access child Stage by its name

        Example:
            >>> from asterstudy.datamodel.history import History
            >>> history = History()
            >>> stage_1 = history.current_case.create_stage("Stage 1")
            >>> stage_2 = history.current_case.create_stage("Stage 2")
            >>> s1 = history.current_case[1]
            >>> s2 = history.current_case["Stage 2"]
            >>> stages = history.current_case[:2]

        Returns:
            Stage, islice: Single Stage or set of Stages for slice
            accessor.
        """
        if isinstance(given, Stage):
            return given

        if isinstance(given, int):
            return self.model.get_node(self._children[given])

        if not isinstance(given, slice):
            return next(stage for stage in self if stage.name == given)

        if isinstance(given.start, Stage):
            return itertools.dropwhile(lambda x: x is not given.start, self)

        if not isinstance(given.stop, Stage):
            return itertools.islice(self, given.stop)

        return itertools.takewhile(lambda x: x is not given.stop, self)

    def __delitem__(self, given):
        """
        Implement deletion of stage `self[key]`.

        See `__getitem__()` for description of arguments (slice not
        supported here).
        """

        stage = self[given]

        stage.delete()

    def create_stage(self, name=None, index=None):
        """Create a new Stage in the Case and insert it at the given position.

        The type of new Stage is the same as of the parent Stage.

        If there is no stages in the case, create a new graphical Stage.

        Arguments:
            name (Optional[str]): Name of new Stage. Defaults to *None*.
            index (int): Position in the stages list. Defaults to *None* that
                means the last position in the list.

        Returns:
            Stage: New Stage.
        """
        if not name or name in [stg.name for stg in self.stages]:
            name = self.new_stage_name(name)

        # current number is assigned within add_stage() method
        stage = Stage(name)
        self.model.add(stage, None)

        self.add_stage(stage, index)

        return stage

    def add_stage(self, stage, index=None):
        """Add Stage in the Case at the given position.

        The type of Stage becomes the same as of the previous Stage.

        Arguments:
            stage (Stage): Stage being added.
            index (int): Position in the stages list. Defaults to *None* that
                means the last position in the list.
        """
        assert stage not in self.stages

        nb_stages = self.nb_stages
        index = nb_stages if index is None else index
        stage.number = index + 1
        for exist in self.stages[index:]:
            exist.number += 1

        # create connections with parent case
        # does nothing if that already exists
        add_parent(stage, self)

        self.sort_children(Stage, 'number')

        if stage.mode is None:
            stage.use_graphical_mode()

    @property
    def stages(self):
        """list[Stage]: Attribute that holds Stages stored in the Case."""
        return [i for i in self.child_nodes if isinstance(i, Stage)]

    @property
    def nb_stages(self):
        """int: Attribute that holds number of Stages in the Case."""
        return len(self.stages)

    @property
    def in_dir(self):
        """str: Attribute that holds *Input* directory of the Case."""
        return self._in_dir

    @in_dir.setter
    def in_dir(self, in_dir):
        if in_dir is not None:
            in_dir = osp.realpath(in_dir)
        if in_dir is not None and self._out_dir is not None:
            if same_path(in_dir, self._out_dir):
                raise ValueError("input and output dirs can't be the same")
            if is_subpath(in_dir, self._out_dir):
                raise ValueError("input dir can't be sub-path of output dir")
            if is_subpath(self._out_dir, in_dir):
                raise ValueError("input dir can't be parent of output dir")
        if in_dir is not None and not osp.exists(in_dir):
            raise ValueError("non-existent directory: '{}'".format(in_dir))
        self._in_dir = in_dir

    @property
    def out_dir(self):
        """str: Attribute that holds *Output* directory of the Case."""
        return self._out_dir

    @out_dir.setter
    def out_dir(self, out_dir):
        if out_dir is not None:
            out_dir = osp.realpath(out_dir)
        if out_dir is not None and self._in_dir is not None:
            if same_path(out_dir, self._in_dir):
                raise ValueError("input and output dirs can't be the same")
            if is_subpath(out_dir, self._in_dir):
                raise ValueError("output dir can't be sub-path of input dir")
            if is_subpath(self._in_dir, out_dir):
                raise ValueError("output dir can't be parent of input dir")
        self._out_dir = out_dir

    def __len__(self):
        """
        Support native Python 'len' operator protocol.
        """
        return self.nb_stages

    def __iter__(self):
        """
        This method is called when an iterator is required for a Case.

        Example:
            >>> from asterstudy.datamodel.history import History
            >>> history = History()
            >>> stage_1 = history.current_case.create_stage("Stage 1")
            >>> stage_2 = history.current_case.create_stage("Stage 2")
            >>> for stage in history.current_case:
            ...     print(stage.name)
            ...
            Stage 1
            Stage 2

        Returns:
            listiterator: Iterator object that allows traversing child
            Stages.
        """
        return iter(self.stages)

    def get_stage_by_num(self, number):
        """
        Get Stage by number.

        Arguments:
            number (int): Stage's number.

        Returns:
            Stage: Child Stage (None if there's no child Stage with such
            number).
        """
        stages = [stage for stage in self.stages if stage.number == number]
        if len(stages) == 1:
            return stages[0]
        return None

    def text2stage(self, text, name=None, strict=ConversionLevel.NoFail,
                   force_text=False, provider=None):
        """
        Create a new stage from a COMM text snippet.

        See `import_stage()` for details about *strict* mode.

        Arguments:
            text (str): COMM code snippet.
            name (str): Name of Stage being created.
            strict (ConversionLevel): Tells how strict the conversion
                must be. For more details, see `general.ConversionLevel`.
                Default is not to fail.
            force_text (Optional[bool]): Keep stages in text mode.
            provider (*FileProvider*): Instance of *FileProvider* that can
                provide additional COMM files on demand.

        Returns:
            Stage: New Stage.
        """
        stage = self.create_stage(name)
        is_graphical_mode = not force_text and stage.is_graphical_mode()
        stage.use_text_mode()
        stage.set_text(text)

        if is_graphical_mode:
            try:
                stage.use_graphical_mode(strict, provider)
            except Exception as exc: # pragma pylint: disable=broad-except
                debug_message('can not use graphical mode: {0}'.format(exc))

        return stage

    def import_stage(self, file_name, strict=ConversionLevel.NoFail,
                     force_text=False, provider=None):
        """
        Create new Stage by importing code_aster COMM file.

        New Stage is created in the same edition mode as the parent
        Stage (if there is any).

        If there is no existing Stage, new Stage is created in a
        graphical mode.

        Note:
            If Stage cannot be converted to graphical mode due to any
            reason, the Stage is created in text mode.

        Arguments:
            file_name (str): Path to the COMM file.
            strict (Optional[ConversionLevel]): Tells how strict the conversion
                must be. For more details, see `general.ConversionLevel`.
                Default is not to fail.
            force_text (Optional[bool]): Keep stages in text mode.
            provider (*FileProvider*): Instance of *FileProvider* that can
                provide additional COMM files on demand.

        Returns:
            Stage: New Stage.
        """
        with open(file_name) as file:
            text = file.read()
        name = osp.splitext(osp.basename(file_name))[0]
        return self.text2stage(text, name, strict, force_text, provider)

    def export(self, export_name, testcase=False, parametric=False):
        """Export case.

        Arguments:
            export_name (str): Filename of export file. Additional files will
                be added into its parent directory.
            testcase (bool): If *True*, export case to prepare a testcase.
            parametric (bool): If *True*, export case for a parametric study.
        """
        from .engine.engine_utils import ExportCase
        export = ExportCase.factory(self, export_name, testcase, parametric)
        export.generate()

    def check(self, mode=Validity.Complete):
        """
        Get validity status of Case.

        Returns:
            bool: Validity status.
        """
        result = Validity.Nothing

        for stage in self:
            result |= stage.check(mode)

        return result

    def repair(self):
        """Try to repair the case in case of dependency error.

        - Search for broken dependencies: commands that are not in the model.

        - Try to fix these broken dependencies by using results with the same
          name and type.

        Returns:
            Validity: Status of the validation of the case after repairing.
        """
        commands_store = set()
        for stage in self:
            stage.repair(commands_store)

        return self.check()

    def is_used_by_others(self):
        """Tells whether a Case's descendant Stages are contained in other
        cases"""
        for stage in self.stages:
            if stage.parent_case is not self:
                continue
            cases = [self]
            if self.model:
                cases.append(self.model.current_case)
            cases = [i for i in stage.cases if i not in cases]
            if cases:
                return True
        return False

    def used_by_others(self):
        """Tells what cases contain descendant Stages from this one"""
        result = set()
        if self.is_used_by_others():
            for stage in self.stages:
                if stage.parent_case is not self:
                    continue
                cases = [self]
                if self.model:
                    cases.append(self.model.current_case)
                cases = [i for i in stage.cases if i not in cases]
                for case in cases:
                    if case.is_backup:
                        continue
                    result.add(case)
                    result.union(case.used_by_others())
        return list(result)

    def restore_stages_mode(self):
        """Restore the Stages to graphical mode if they were in graphical mode
        before being saved.
        """
        msg = "Restore stage '{0}:{{0}}' to graphical mode...".format(self.name)
        for stage in self.stages:
            was = stage.saving_mode
            if was != stage.mode and was == DataSet.graphicalMode:
                info_message(msg.format(stage.name))
                stage.use_graphical_mode()

    @classmethod
    def use_default_naming(cls):
        """Enable the default naming of command results."""
        cls.naming_system = Case.autoNaming

    @classmethod
    def use_basic_naming(cls):
        """Switch to a basic naming of command results."""
        cls.naming_system = Case.basicNaming

    def generate_name(self, command, check_previous=False):
        """Generate the name for the command.

        Arguments:
            command (Command): A command.
            check_previous (bool): prevent naming conflicts with previous
                commands. Only works if the command is already aware of
                its stage.

        Returns:
            str: Name for the command.
        """
        typ = command.safe_type()
        if not typ:
            return "_"

        if self.naming_system == Case.basicNaming:
            return command.title

        try:
            key = typ.getType().lower().replace("_sdaster", "")
            prefix = SD_DICT.get(key, "unnamed")
        except (TypeError, AttributeError):
            prefix = "unnamed"

        attempts = [""] + list(range(1000))
        prenames = []
        if check_previous:
            prenames = command.previous_names()
            prenames.add(command.name)
        while attempts:
            suffix = str(attempts.pop(0))
            size = 8 - len(suffix)
            name = "{0}{1}".format(prefix[:size], suffix)
            if name not in self._generated_names and name not in prenames:
                self._generated_names.add(name)
                return name

        return prefix + "_XXX"

    def before_remove(self):
        """Deletes a case, or more precisely all cases that have common
        descendants with this one.
        """
        referencing_cases = self.used_by_others()

        # check if case can be removed
        RCaseMixing.before_remove(self)

        # delete directory
        self.delete_dir()

        # retrieve cases with common descendants
        return (referencing_cases,)

    def after_remove(self, referencing_cases): # pragma pylint: disable=arguments-differ
        """Hook that is called after the node removing is finished."""
        for case in referencing_cases:
            case.delete()

    def copy_shared_stages_from(self, number, context=Ctx.Nothing):
        """
        Recursively copies all referenced stages from *number*
        that are shared by several cases.

        See the drawing below.

        Arguments:
            number (int): stage number from where to start.
        """
        # Before the operation
        #
        #   -------------  ---------------
        #   |   self    |  |    other    | <= parent case: cases[0].
        #   -------------  --------------
        #      ^  ^    ^    ^       ^  ^
        #      |   \ [1]\   |[0]     \  \
        #      |    \    \  |         \  \
        #      |     \     ---------   \  \
        #       \     \    | stage1 |   | |
        #        \     \   ----------  /  |
        #         \     \             /   |
        #          \  [1]\           /[0] |
        #           \      ---------/    /
        #            \     | stage2 |   /
        #             \    ----------  /
        #           [1]\              /[0]
        #               \            /
        #                  ---------
        #                  | stage3 |
        #                  ----------
        #
        # After the operation self.copy_shared_stages_from(2)
        #
        #   -------------  ---------------
        #   |   self    |  |    other    |
        #   -------------  --------------
        #    ^    ^    ^    ^       ^  ^
        #   /     |  [1]\   |[0]     \  \
        #  /      |      \  |         \  \
        #  |      |        ---------   \  \
        #  |      |        | stage1 |   | |
        #  |      |        ----------  /  |
        #  |      |                   /   |
        #  |      |[0]               /[0] |
        #  |  ---------    ---------/    /
        #  |  | st2'  |    | stage2 |   /
        #  |  ---------    ----------  /
        #   \[0]                      /[0]
        #    \                       /
        #     ---------     ---------
        #     | st3'  |    | stage3 |
        #     ---------    ----------
        #
        # Index of first stage referencing only `self`
        first_exclusive = self.first_exclusive()

        # Iterator with all stages to copy
        # (those referencing other cases and with index > number)
        start = first_exclusive if first_exclusive >= 0 else self.nb_stages
        iterator = (self[i-1] for i in range(start, number - 1, -1))

        # Copy stages in reversed order
        for stage in iterator:
            stage.copy(self, context)
            # As this is reversed copy,
            # do not forget to reorder each time
            self.sort_children(Stage, 'number')

    def first_exclusive(self):
        """
        Index of first stage referencing only `self` if any, else -1
        """
        owned_list = [i for i in range(self.nb_stages) \
                          if self[i].parent_case is self]
        return owned_list[0] if owned_list else -1

    def detach(self, stage):
        """
        Detach stage from case

        Arguments:
            stage: stage to be detached.
                   Can be *int*, *str* or *Stage*, but not a slice.

        Raises:
            ValueError: if `stage` is not referenced
        """
        if stage not in self:
            return

        # if the last one, detach it
        # otherwise, call the function recursively on next stage
        mystage = self[stage]
        if mystage is not self.stages[-1]:
            self.detach(self[mystage.number])
        self._detach_last()

        # if `stage` references only the current case,
        # then reinitialize its *Result* object
        if len(mystage.cases) == 1:
            if mystage.parent_case is mystage.model.current_case:
                mystage.result.clear()


    def _detach_last(self):
        """Detach the last stage of `self`."""

        last_stage = self.stages[-1]
        other_cases = [c for c in last_stage.cases if c is not self]
        if other_cases:
            # simply a refence to remove
            remove_parent(last_stage, self)
            # no need to reorder, since we removed the last one
        else:
            # delete the object
            last_stage.delete()

    def can_be_ran(self):
        """Tells whether this case is valid for running."""
        return self.nb_stages > 0 and self.check() == Validity.Nothing

    @property
    def variables(self):
        """Return all known *Variable* objects defined in a Case in the order
        of their definition.

        Returns:
            OrderedDict{name: variable}: Existing Python variables.
        """
        lvar = []
        for stage in self.stages:
            lvar.extend([(cmd.name, cmd) for cmd in stage.sorted_commands
                         if isinstance(cmd, Variable)])
        return OrderedDict(lvar)

    @property
    def job_infos(self):
        """*JobInfos*: Attribute that holds the 'job_infos'
        property."""
        return self._job_infos

    @job_infos.setter
    def job_infos(self, value):
        self._job_infos = value

    def accept(self, visitor):
        """
        Walk along the objects tree using the visitor pattern.

        Arguments:
            visitor (any): Visitor object.
        """
        visitor.visit_case(self)

    def new_stage_name(self, root):
        """Returns an inexisting name for a stage.

        Arguments:
            root (str): Root for the new stage. If *None*, "Stage" is used.

        Returns:
            str: Name based on *root* that doesn't yet exist in children.
        """
        return self.model.new_name(root or "Stage", self.stages)

    def relocate_result_files(self, fromdir):
        """Relocate the result files that are located under `fromdir`
        into the new directory of `case`.

        The relative path is preserved.
        Example: ``/old/path/Study_Files/result.med`` will be
        ``/new/path/NewName_Files/result.med``.
        The existing files are not renamed on disk, only in the Datafiles tab.
        The data files are unchanged.

        Arguments:
            case (Case): Top level object (should be the *CurrentCase*).
            fromdir (str): Original directory.
        """
        basedir = self.model.folder
        fromdir = fromdir.rstrip(os.sep) + os.sep
        for stage in self.stages:
            for info in stage.handle2info.values():
                if info.attr & FileAttr.Out:
                    fname = info.filename
                    if fname and fname.startswith(fromdir):
                        new = fname.replace(fromdir, '')
                        info.filename = osp.join(basedir, new)
                        info_message("New result file name:", info.filename)
