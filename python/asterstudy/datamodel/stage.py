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
Stage
-----

Implementation of a stage within the study case.

"""


# The pragma below has to be removed after migration to Python 3 and
# suppression of above two lines.
# pragma pylint: disable=wrong-import-position,wrong-import-order

from functools import wraps

from ..common import (ConversionError, format_code, no_new_attributes, to_unicode)
from ..common.conversion import ConversionReport
from .abstract_data_model import Node, add_parent, remove_parent
from .aster_parser import add_debut_fin
from .comm2study import comm2study
from .command import ModifiesStageInstance as ModifiesInstance
from .command import Command, paths_using_group
from .dataset import DataSet
from .file_descriptors import Mixing as FDMixing
from .general import CopyContext as Ctx
from .general import ConversionLevel, Validity
from .result import StageMixing as RStageMixing
from .study2comm import study2comm


def only_on(mode):
    """
    Decorator to check that the Stage object is in graphical/text mode.

    Arguments:
        method (method): Object's wrapped method.
        mode (str): Required mode: "graphical" or "text".
    """
    def wrapped_method(method):
        """Decorate the method of *Stage*."""
        @wraps(method)
        def wrapper(self, *args, **kwds):
            """wrapper"""
            if (mode == "graphical" and not self.is_graphical_mode()) or \
                    (mode == "text" and not self.is_text_mode()):
                raise TypeError("Not allowed in {} mode".format(mode))
            return method(self, *args, **kwds)
        return wrapper
    return wrapped_method


class UsageOptions:
    """Enumerator for specific usages of a Stage.

    Attributes:
        Default: For a standard execution of a Stage.
        LoadDataBase: Stage used to initialize a Case from a database.
    """
    Default = 0x00
    LoadDatabase = 0x01


class Stage(Node, FDMixing, RStageMixing):
    """Implementation of the stage.

    A Stage has a restricted number of children:

    - one child of type DataSet (GraphicalDataSet or TextDataSet).
    - one child of type Result.
    """
    _number = _dataset = _conv_report = _savingmode = _usage = _dbase = None
    __setattr__ = no_new_attributes(object.__setattr__)

    def __init__(self, name, number=0):
        """
        Create Stage object.

        Arguments:
            name (str): Name of a Stage.
            number (Optional[int]): Ordinal number of Stage within
                parent Case. Defaults to 0.
        """
        RStageMixing.__init__(self)
        Node.__init__(self, name)
        FDMixing.__init__(self)

        self._number = number
        self._dataset = None
        self._conv_report = None
        self._savingmode = None
        self._usage = UsageOptions.Default

        self.deep_copy = DataSet

    def __getstate__(self):
        """Reset attached exception before pickling."""
        self._conv_report = None
        return self.__dict__

    @property
    def number(self):
        """int: Attribute that holds the index number of the Stage
        in the parent Case."""
        return self._number

    @number.setter
    def number(self, number):
        self._number = number

    @property
    def parent_case(self):
        """Case: Attribute that holds the parent Case owning this
        Stage."""
        cases = self.cases
        return cases[0] if cases else None

    @property
    def cases(self):
        """list[Case]: Attribute that holds all cases which contain this
        Stage."""
        from .case import Case
        return [i for i in self.parent_nodes if isinstance(i, Case)]

    @property
    def child_stages(self):
        """list[Stage]: Attribute that holds child Stages of this
        Stage."""
        return [c[self.number] for c in self.model.cases
                if c.nb_stages > self.number and c[self.number-1] is self]

    @property
    def parent_stage(self):
        """list[Stage]: Attribute that holds the parent stage of this
        Stage."""
        if self.number > 1:
            return self.parent_case[self.number-2]
        return None

    @property
    def dataset(self):
        """DataSet: Attribute that holds the Stage's DataSet."""
        if self._dataset is not None:
            return self._dataset

        objects = [child for child in self.child_nodes \
                   if isinstance(child, DataSet)]

        # assert objects, "DataSet is not yet initialized!"
        if not objects:
            # the DataSet is not yet initialized!
            return None

        assert len(objects) == 1, "too much DataSet children!"
        self._dataset = objects[0]

        return self._dataset

    @dataset.setter
    def dataset(self, dataset):
        """Assign or replace the dataset object."""
        if self._dataset is not None:
            self._dataset.delete()

        if dataset is not None:
            self._dataset = self._model.add(dataset, self)

    @property
    def mode(self):
        """int: Attribute that holds a type of Stage
        (see *DataSet.mode()*)."""
        return self.dataset.mode if self.dataset is not None else None

    @property
    def saving_mode(self):
        """int: Attribute that holds the type of the Stage at saving time.

        Reloading a Study, all stages of RunCases stay in text mode.
        Their *saving_mode* is the mode when the user edits them.
        If the Stage hasn't not been loaded from JSON, it will be as *mode*.
        """
        return self._savingmode if self._savingmode is not None else self.mode

    @saving_mode.setter
    def saving_mode(self, value):
        """Setter for *saving_mode*."""
        self._savingmode = value

    @Node.name.setter # pragma pylint: disable=no-member
    @ModifiesInstance(True)
    def name(self, name):
        """Redefine name setter in order to decorate it"""
        # I am compelled to copy the content of Node.name.setter here
        if self._name != name:
            self._name = name
            self._after_rename()

    @property
    def usage(self):
        """UsageOptions: Attribute that holds the stage usage."""
        return self._usage

    @usage.setter
    def usage(self, value):
        self._usage = value

    @property
    def database(self):
        """str: Attribute that holds the database path in case of
        initialization from a database (first stage only)."""
        return self._dbase

    @database.setter
    def database(self, path):
        if self._number != 1:
            raise ValueError("'database' is only available for the first stage")
        self._dbase = path

    def accept(self, visitor):
        """
        Walk along the objects tree using the visitor pattern.

        Arguments:
            visitor (any): Visitor object.
        """
        visitor.visit_stage(self)

    def use_graphical_mode(self, strict=ConversionLevel.NoFail, provider=None):
        """
        Convert the child *DataSet* in a graphical one.

        If the current *DataSet* is not initialized, it is created.

        Does nothing if the DataSet is already a graphical one.

        Arguments:
            strict (Optional[ConversionLevel]): Tells how strict the conversion
                must be. For more details, see `general.ConversionLevel`.
                Default is not to fail.
            provider (*FileProvider*): Instance of *FileProvider* that can
                provide additional COMM files on demand.

        Raises:
            TypeError: If parent Stage is a text one;
            comm2study.ConversionError: If the import fails.
        """
        self.reset_conv()
        if self.dataset is None:
            self.dataset = DataSet.factory(DataSet.graphicalMode)
            return

        if self.is_graphical_mode():
            return

        self._2graphical(strict, provider)

    @ModifiesInstance(True)
    def _2graphical(self, strict, provider):
        """
        conversion to graphical, once all checks done
        """
        previous = self.dataset
        dataset = DataSet.factory(DataSet.graphicalMode)
        self._dataset = self._model.add(dataset, self)
        self._conv_report = ConversionReport()
        try:
            comm2study(previous.text, self, strict=strict, provider=provider,
                       report=self._conv_report)
            self.track_unused()
        except ConversionError:
            self._dataset = previous
            dataset.delete()
            raise

        previous.delete()

    def paste(self, snippet):
        """Pastes the given text Code-Aster snippet at the tail of the stage"""
        result = []

        # If the stage is in graphical mode, it is converted to text mode.
        # But not the subsequent ones
        # (now graphical stages can follow text ones).
        current_mode = self.mode
        if current_mode == DataSet.graphicalMode:
            num = len(self)
            last = self[num - 1] if num else None
            self.text_mode_on()

        # Append snippet at the end of existing (freshly converted) text
        current_text = self.get_text()
        if current_text.endswith('\n') or snippet.startswith('\n'):
            text = current_text + snippet
        else:
            text = current_text + '\n' + snippet

        self.set_text(text)

        if current_mode != DataSet.graphicalMode:
            result.append(self)
            return result

        # Try to convert back to graphical
        try:
            self.use_graphical_mode()
        except Exception as exc:
            self.set_text(current_text)
            self.use_graphical_mode()
            raise exc

        # Repair potential broken dependencies in child stages
        # So we call repair on the whole case
        self.parent_case.repair()

        # Does not return pasted objects rigorously
        # (commands are reordered at the end of comm2study)
        # But returns something indicating if operation was successful
        for i in range(num, len(self)):
            result.append(self[i])

        if not result:
            new_num = len(self)
            new_last = self[new_num - 1] if new_num else None
            if last is not None and new_last is not None:
                try:
                    last * new_last
                except AssertionError:
                    result.append(new_last)

        return result

    def text_mode_on(self):
        """
        Convert the child *DataSet* in a text one.

        If the current *DataSet* is not initialized, it is created.

        Does nothing if the DataSet is already a text one.

        Raises:
            TypeError: If parent Stage is a graphical one.
        """
        self.reset_conv()

        if self.is_text_mode():
            return

        self._2text()

    def use_text_mode(self):
        """
        Convert the child *DataSet* in a text one.

        If the current *DataSet* is not initialized, it is created.

        Does nothing if the DataSet is already a text one.

        Raises:
            TypeError: If parent Stage is a graphical one.
        """
        self.text_mode_on()

        return self

    @ModifiesInstance(True)
    def _2text(self):
        """
        Conversion to text, once all checks have been done
        """
        previous = self.dataset
        text = study2comm(previous)

        self.text_filedesc()

        # Create a new empty text dataset
        # Apparently, command objects are no longer deleted
        dataset = DataSet.factory(DataSet.textMode)
        self._dataset = self._model.add(dataset, self)

        # All children to the previous (graphical) DataSet
        #     are transferred to the new (text) DataSet.
        for child in previous.child_nodes:
            remove_parent(child, previous)
            add_parent(child, dataset)
            if isinstance(child, Command):
                child.reset_validity()

        # Old graphical dataset removed from model
        self._model.unregister(previous)
        remove_parent(previous, self)
        previous.detach_model()

        dataset.text = text

    def is_graphical_mode(self):
        """
        Tell if the Stage is currently based on a GraphicalDataSet.

        Returns:
            bool: *True* if Stage is graphical one; *False* otherwise.
        """
        return self.dataset is not None and self.dataset.is_graphical_mode()

    def is_text_mode(self):
        """
        Tell if the Stage is currently based on a TextDataSet.

        Returns:
            bool: *True* if Stage is text one; *False* otherwise.
        """
        return self.dataset is not None and self.dataset.is_text_mode()

    @ModifiesInstance(True)
    def rename(self, name):
        """
        Rename the Stage.

        Arguments:
            name (str): New name.
        """
        self.name = name

    def name_exists(self, name):
        """Tell if `name` is an existing Stage name.

        Arguments:
            name (str): Proposed name.

        Returns:
            bool: *True* if another Stage with this name already exists.
        """
        return name in [i.name for i in self.parent_case.stages
                        if i is not self]

    @ModifiesInstance(False)
    def copy(self, parent_case=None, context=Ctx.Nothing):
        """
        Create a copy of this Stage.

        Arguments:
            parent_case (Optional[Case]): Case to which the new Stage
                shall be related. Defaults to *None*.

        Returns:
            Stage: A copy of this Stage.
        """
        return self._model.copy(self,
                                parent_case=parent_case,
                                context=context)

    def initialize_copy(self):
        """
        Bare copy: Create new empty Stage.

        Hook function: called when this Stage is copied.

        Returns:
            Stage: New empty Stage.
        """
        return Stage(self.name, self.number)


    def customize_copy(self, orig, **kwargs):
        """
        Hook: Attune data model additionally after a Stage
        has been copied, before the Commands inside it are copied.

        Updates relationship of the newly created stage.

        After copy this new stage (*self*):

        - has the *parent_case* of *orig*;
        - is a child all the parents of *orig*;
        - is a child of *parent_case* passed to *copy()*.

        Useful when modifying a stage.

        Arguments:
            orig (Stage): the original Stage object freshly replicated.
            parent_case (Optional[Case]): Case to which the Stage shall
                be related. Defaults to *None*.
            context (Ctx): Context of copy.
        """
        parent_case = kwargs.get('parent_case')
        context = kwargs.get('context', Ctx.Nothing)

        # remove all parent cases
        for parent in self.cases:
            remove_parent(self, parent)

        # add relation new case -> new stage
        add_parent(self, parent_case)

        if parent_case is None:
            return

        # remove relationship new case -> old stage
        remove_parent(orig, parent_case)

        if context & Ctx.AutoCopy:
            # switch results between orig and self
            self.result, orig.result = orig.result, self.result

            # result contains a ref to the stage, to be switched as well
            self.result.stage, orig.result.stage = \
            orig.result.stage, self.result.stage


    def finalize_copy(self, orig, **kwargs):
        """
        Hook: Attune data model additionally after a Stage
        has been copied, after the commands inside it
        have been copied.

        Creates copies of file objects and embedded files.

        Arguments:
            orig (Stage): the original Stage object freshly replicated.
            context (Ctx): Context of copy.
        """
        parent_case = kwargs.get('parent_case')
        context = kwargs.get('context', Ctx.Nothing)
        # copy datafiles, reassociate commands?
        for handle, info in orig.handle2info.items():
            new = self.handle2info[handle]
            new.copy_from(info)

        if parent_case is None:
            return

        if context & Ctx.AutoCopy:
            # copy embedded files to the new location
            orig.copy2tmpdir()

    #@profile_method('out_', show_graph=True)
    @ModifiesInstance(False)
    def autocopy(self):
        """
        If `self` references several cases, creates a copy. Child stages
            referencing several cases are copied as well.
        Originals are referenced by the current case. Copies are
            referenced by the other cases (runcases).
        """
        current_case = self.model.current_case
        self._autocopy_algo(current_case)

    def _autocopy_algo(self, current_case):
        """
        Algorithm for the above.
        """
        # Only stages referenced by at least one runcase
        #     should be copied.
        parent_case = self.parent_case
        if current_case is parent_case:
            return
        # As in `copy_shared_stages_from`
        # stages should be copied in reversed order
        if self.number != current_case.nb_stages:
            last_stage = current_case[self.number]
            last_stage._autocopy_algo(current_case) # pragma pylint: disable=protected-access

        self._autocopy_stage(parent_case, current_case)

    def _autocopy_stage(self, parent_case, current_case):
        """
        Utility method: copies `self` so that `parent_case` and
            `current_case` no longer share the same instance.

        Warning: there are conditions to call this method:
            - `parent_case` and `current_case` should be distinct
            - child stages to `self` should not be shared
                  between `parent_case` and `current_case`

        See the drawing below
        """
        # Before the operation
        #             parent case: cases[0] ------
        #                                        v
        #   -------------  ------------     --------------
        #   | current   |  | other    |     |    parent    |
        #   -------------  -----------      --------------
        #    ^    ^    ^        ^                    ^
        #    |     \ [2]\       |                    |
        #    |      \    \      |                    |
        #    |       \    \     |   [1]     -------- |
        #    |        \    -----------------|stage1|-|[0]
        #    |         \        |           -------- |
        #    |          \       |                    |
        #    |        [2]\      |                    |
        #    |            \     |   [1]     -------- |
        #    |             -----------------|stage2|-|[0]
        #    |                  |           -------- |
        #    |[0]               |                    |
        #    |                  |                    |
        #  --------             |   [1]     -------- |
        #  |stage3|             ------------|st3'  |-|[0]
        #  --------                         --------
        #
        # After the operation stage2._autocopy_stage(parent, current)
        #
        #             parent case: cases[0] ------
        #                                        v
        #   -------------  ------------     --------------
        #   | current   |  | other    |     |    parent    |
        #   -------------  -----------      --------------
        #    ^  ^      ^        ^                    ^
        #    |  |    [2]\       |                    |
        #   /   |        \      |                    |
        #  /    |         \     |   [1]     -------- |
        # /     |          -----------------|stage1|-|[0]
        #/      |               |           -------- |
        #|      |[0]            |                    |
        #|      |               |                    |
        #|  --------            |   [1]     -------- |
        #|  |stage2|            ------------|st2'  |-|[0]
        #|  --------            |           -------- |
        # \                     |                    |
        #  \[0]                 |                    |
        #   --------            |   [1]     -------- |
        #   |stage3|            ------------|st3'  |-|[0]
        #   --------                         --------
        #
        original = []

        assert parent_case is not current_case

        # make the current_case the new parent
        #   -------------  ---------------  --------------
        #   | current   |  |    other    |  |    parent    |
        #   -------------  --------------   --------------
        #    ^                          ^            ^
        #    |                          |            |
        #    |                          |            |
        #    | ---------             [2]|        [1] |
        # [0]|-| stage1 |---------------|-------------
        #    | ----------               |            |
        #    |                          |            |
        #    |                          |            |
        #    | ---------             [2]|        [1] |
        # [0]|-| stage2 |---------------|-------------
        #    | ----------               |            |
        #    |                          |            |
        # [0]|                          |            |
        #   ---------                [1]|   -------  |
        #   | stage3 |                  |---| st3' |-|[0]
        #   ---------                       -------
        for stage in reversed(parent_case.stages):
            original.append((stage, stage.parent_case))
            stage.move_parent(current_case, 0)
            assert stage.parent_case is current_case \
                or stage not in current_case

        # make `parent` own stage2
        #   -------------  ---------------  --------------
        #   | current   |  |    other    |  |    parent    |
        #   -------------  --------------   --------------
        #    ^                          ^            ^
        #    |                          |            |
        #    |                          |            |
        #    | ---------             [2]|        [1] |
        # [0]|-| stage1 |---------------|-------------
        #    | ----------               |            |
        #    |                          |            |
        #    |                          |            |
        #    | ---------             [1]|     ------ |
        # [0]|-| stage2 |---------------|     |st2'|-|[0]
        #    | ----------               |     ------ |
        #    |                          |            |
        # [0]|                          |            |
        #   ---------                [1]|     -----  |
        #   | stage3 |                  |-----|st3'|-|[0]
        #   ---------                         -----
        parent_case.copy_shared_stages_from(self.number, context=Ctx.AutoCopy)

        # return to earlier parentship
        #   -------------  ---------------  --------------
        #   | current   |  |    other    |  |    parent    |
        #   -------------  --------------   --------------
        #    ^         ^                ^            ^
        #    |          \               |            |
        #    |           \              |            |
        #    |            \[2]       [1]| ---------  |
        # [0]|             ---------------| stage1 |--[0]
        #    |                          | ---------- |
        #    |                          |            |
        #    |                          |            |
        #    | ---------             [1]|     ------ |
        # [0]|-| stage2 |---------------|     |st2'|-|[0]
        #    | ----------               |     ------ |
        #    |                          |            |
        # [0]|                          |            |
        #   ---------                [1]|     -----  |
        #   | stage3 |                  |-----|st3'|-|[0]
        #   ---------                         -----
        for stage, parent in original:
            stage.move_parent(parent, 0)
            # Ensure that current is still the last referenced case
            if stage in current_case.stages:
                remove_parent(stage, current_case)
                add_parent(stage, current_case)
                current_case.sort_children(type(stage), 'number')

        # make `other` point to `st2'` instead of `stage2`
        #   -------------  ---------------  --------------
        #   | current   |  |    other    |  |    parent    |
        #   -------------  --------------   --------------
        #    ^         ^                ^            ^
        #    |          \               |            |
        #    |           \              |            |
        #    |            \[2]       [1]| ---------  |
        # [0]|             ---------------| stage1 |--[0]
        #    |                          | ---------- |
        #    |                          |            |
        #    |                          |            |
        #    | ---------             [1]|     ------ |
        # [0]|-| stage2 |               |-----|st2'|-|[0]
        #    | ----------               |     ------ |
        #    |                          |            |
        # [0]|                          |            |
        #   ---------                [1]|     -----  |
        #   | stage3 |                  |-----|st3'|-|[0]
        #   ---------                         ------
        nb_stages = min(parent_case.nb_stages, current_case.nb_stages)
        for i in range(self.number-1, nb_stages):
            stage = current_case[i]
            clist = [k for k in stage.cases if k is not current_case]
            for other in clist:
                remove_parent(stage, other)
                add_parent(parent_case[i], other)
                other.sort_children(type(stage), 'number')

    @only_on("graphical")
    def clear(self):
        """Clear stage."""
        self.dataset.clear()

    # shortcuts to GraphicalDataSet methods
    @ModifiesInstance(True)
    def add_command(self, command_type, name=None):
        """
        Add a command into the dataset.

        Arguments:
            command_type (str): Type of the command (in a catalogue).
            name (Optional[str]): Name of the command. Defaults to
                *None*; in this case name is automatically generated for
                the command.

        Returns:
            Command: New command.

        See `GraphicalDataSet.add_command()`.
        """
        return self.dataset.add_command(command_type, name)

    @ModifiesInstance(True)
    def add_variable(self, var_name, var_expr=''):
        """Add a variable into the dataset.

        Arguments:
            var_name (str): Name of the variable.
            var_expr (str): Right side variable expression.

        Returns:
            Variable: Variable just added.

        See `GraphicalDataSet.add_variable()`.
        """
        return self.dataset.add_variable(var_name, var_expr)

    @only_on("graphical")
    @ModifiesInstance(True)
    def add_comment(self, content, concatenate=True):
        """Add a Comment instance into the dataset.

        Arguments:
            content (str): content of the (optionaly multiline) Comment.

        Returns:
            Comment: Comment just added.

        See `GraphicalDataSet.add_comment()`.
        """
        return self.dataset.add_comment(content, concatenate)

    @only_on("graphical")
    @ModifiesInstance(True)
    def __call__(self, command_type, name='_'):
        """
        Add a command into the dataset.

        See `add_command()` for description of arguments.
        """
        return self.dataset.add_command(command_type, name)

    @only_on("text")
    @ModifiesInstance(True)
    def update_commands(self, defs):
        """Update the commands returned by the text dataset.

        Arguments:
            defs (list[(str, str, str)]): List of the definitions of the
                commands: *(name, title, type)*.

        See `GraphicalDataSet.update_commands()`.
        """
        self.dataset.update_commands(defs)
        self.reset_validity()

    @only_on("text")
    @ModifiesInstance(True)
    def delete_commands(self, dels):
        """Update the list of commands deleted by the text dataset.

        Arguments:
            dels (list[str]): List of the names of the deleted commands.

        See `GraphicalDataSet.delete_commands()`.
        """
        self.dataset.delete_commands(dels)
        self.reset_validity()

    def on_remove_command(self, command):
        """
        Remove the command from the dataset.

        Arguments:
            command (Command): Command being removed.
        """
        if self.is_graphical_mode():
            self.dataset.on_remove_command(command)

    def __delitem__(self, item):
        """
        Remove the command from the dataset.

        Arguments:
            command (Command, str): Command being removed.

        See `remove_command()` for arguments description.
        """
        if isinstance(item, Command):
            item.delete()
        else:
            self[item].delete()

    @property
    def commands(self):
        """
        Get all commands of the dataset.

        Returns:
            list[Command]: Commands contained in a Stage.
        """
        return self.dataset.commands

    @property
    def sorted_commands(self):
        """
        Get all commands of the dataset.

        Returns:
            list[Command]: Commands contained in a Stage.
        """
        return self.dataset.sorted_commands

    def preceding_commands(self, command, only_preceding=False):
        """Returns all commands that exist before *command*. More precisely
        these are the commands that do not depend on *command*.

        Arguments:
            command (Command): The Command for which one searches its
                predecessors. If *None*, returns all commands.
            only_preceding (bool): If *True* only returns the commands from the
                preceding stages, not from the current. If *False* all the
                existing commands are returned.

        Returns:
            list[Command]: List of commands.
        """
        commands = []
        if self.parent_stage:
            commands = self.parent_stage.preceding_commands(command)

        if only_preceding:
            return commands

        def _predicate(cmd):
            return (cmd.active and
                    (command is None or not cmd.depends_on(command)))

        local = [cmd for cmd in self.sorted_commands if _predicate(cmd)]

        for cmd in local:
            commands.append(cmd)
            deleted = cmd.deletes()
            if deleted:
                for current in list(commands): # iterate on a copy
                    if current in deleted:
                        commands.remove(current)

        return commands

    def get_cmd_by_index(self, index):
        """Get Command by index.

        Arguments:
            index (int): Command's index (starts from 0).

        Returns:
            Command: Command or *None* if *index* is greater than the number
                of command in the Stage.
        """
        cmds = self.sorted_commands
        if index < len(cmds):
            return cmds[index]
        return None

    @staticmethod
    def add_dependency(node, parent):
        """
        Add a dependency of *node* to *parent*.

        Just a shortcut to simplify usage of *study2code* API.
        """
        add_parent(node, parent)

    @only_on("graphical")
    def reorder(self, command=None):
        """Ask reordering.

        If *command* is not provided all the stage is reordered, else only
        the position of *command* is checked.
        It does nothing on a text stage.
        """
        self.dataset.reorder(command)

    @only_on("graphical")
    def copy2str(self, given):
        """
        Returns command at the 'given' position in terms of code_aster syntax

        See `Stage.__getitem__()` and `Command.__str__`.
        """
        return str(self[given])

    def __iter__(self):
        """
        This method is called when an iterator is required for a Stage.

        Returns:
            listiterator: Iterator object that allows traversing child
            Commands.
        """
        return iter(self.dataset)

    def __contains__(self, given):
        """
        Support native Python "in" operator protocol.

        Arguments:
            given (Command or str): Command being checked.

        Returns:
            bool: *True* if Command is contained in the Stage; *False*
            otherwise.
        """
        return given in self.dataset

    def __getitem__(self, given):
        """
        Support native Python '[]' operator protocol.

        See `GraphicalDataSet.__getitem__()`.
        """
        return self.dataset[given]

    @property
    def nb_commands(self):
        """The number of commands stored in the stage.

        Returns:
            int: The number of commands stored in the stage.
        """
        return len(self.dataset.commands)

    def __len__(self):
        """
        Get Stage length which is:

        - A number of Commands if Stage is a graphical one;
        - A number of text lines if Stage is a text one.

        Returns:
            int: Stage's length.
        """
        return len(self.dataset)

    def is_empty(self):
        """Tell if the *DataSet* is empty (i.e. has no command or no text).

        Returns:
            bool: *True* if the *DataSet* is empty, *False* otherwise.
        """
        return len(self) == 0

    def __mul__(self, other):
        """Support native Python '*' operator protocol."""
        FDMixing.__mul__(self, other)

        RStageMixing.__mul__(self, other)

        ldataset = self.dataset
        rdataset = other.dataset

        # may be graphical?
        maybe_gr = min(self.mode, self.saving_mode)
        maybe_gr_oth = min(other.mode, other.saving_mode)
        assert ldataset.mode == rdataset.mode or maybe_gr == maybe_gr_oth

        assert ldataset * rdataset is None

    @property
    def preceding_stages(self):
        """list[Stage]: Attribute that gives access to the preceding
        Stages."""
        return self.dataset.preceding_stages

    # shortcuts to TextDataSet methods
    @only_on("text")
    @ModifiesInstance(True)
    def set_text(self, text):
        """
        Set the text content of the dataset.

        Arguments:
            text (str): Text being set to the Stage.
        """
        self.dataset.text = text

    @only_on("text")
    @ModifiesInstance(True)
    def append_text(self, text):
        """
        Append text to the dataset content.

        Arguments:
            text (str): Text being appended to the Stage.
        """
        self.dataset.append_text(text)

    def get_text(self, support=None, sort=True, pretty=True, pretty_text=False,
                 add_ids=False, format_id=0, parametric=False):
        """
        Get text content from the dataset.

        Arguments:
            support (Optional[Features]): Supported features of target version.
                This argument should be provided only if the target version is
                not the one used for edition.
            sort (Optional[bool]): Commands are automatically sorted by
                dependency if *True*.
            pretty (Optional[bool]): Optionaly reformat the text for a
                graphical stage.
            pretty_text (Optional[bool]): Optionaly reformat the text for a
                text stage. Should be used for conversions.
            add_ids (Optional[bool]): If *True*, the Command ids will be
                exported in the commands file.
            parametric (Optional[bool]): If *True*, replace Python variables
                by a function call.

        Returns:
            str: Text assigned to the Stage.
        """
        if self.is_graphical_mode():
            text = study2comm(self, support, pretty, sort=sort,
                              add_ids=add_ids, format_id=format_id,
                              parametric=parametric)
        else:
            text = self.dataset.text
            try:
                text = text if not pretty_text else format_code(text)
            except SyntaxError:
                pass
        return text

    def export(self, file_name, lang=None):
        """
        Export Stage to a COMM file.

        Arguments:
            file_name (str): Path to the COMM file.
            lang (str): Language to be used or *None*.
        """
        utext = to_unicode(add_debut_fin(self.get_text(),
                                         self._number == 1, lang))
        if not utext.endswith('\n'):
            utext += '\n'

        with open(file_name, 'w', encoding='utf-8') as handle:
            handle.write(utext)
            handle.flush()

    def check(self, mode=Validity.Complete):
        """
        Get validity status of Stage.

        Returns:
            bool: Validity status.
        """
        result = Validity.Nothing

        # ensure that the commands are well ordered before processing DETRUIRE
        for command in self:
            result |= command.check(mode)

        return result

    @ModifiesInstance(False)
    def delete(self, user_deletion=False):
        """Stage deletion.

        Arguments:
            user_deletion (bool): *True* if individual stage deletion
                from the user, *False* if deletion resulting
                from some other operation.
        """
        # if user deletion, this is necessarily from current
        if user_deletion:
            self.model.current_case.detach(self)
        else:
            Node.delete(self)

    @ModifiesInstance(False)
    def delete_empty(self):
        """Delete the Stage if it is empty (no commands in its dataset)."""
        # Allow to remove the stage if it has no commands in its dataset
        # and if it belongs to only the current case
        if len(self.cases) == 1 and self.dataset.is_empty():
            case = self.parent_case
            for stage in case.stages[self.number:]:
                stage.number -= 1

            remove_parent(self, case)
            self.delete()

    def before_remove(self):
        """Prepare for stage removing."""
        RStageMixing.before_remove(self)
        self.dataset = None
        return Node.before_remove(self)

    def repair(self, previous_commands):
        """Try to repair the stage in case of dependency error.

        - Search for broken dependencies: commands that are not in the model.

        - Try to fix these broken dependencies by using results with the same
          name and type.

        Arguments:
            previous_commands (set): List of commands that previously exist.
        """
        if self.is_text_mode():
            return

        for command in self.sorted_commands:
            # Handle DETRUIRE: refuse commands deleted by DETRUIRE
            # as potential parents.
            for rmcmd in command.deletes():
                previous_commands.discard(rmcmd)

            command.repair(previous_commands)
            previous_commands.add(command)

    def reset_conv(self):
        """Reset the conversion report."""
        self._conv_report = None

    @property
    def conversion_report(self):
        """Property that holds the last conversion report."""
        return self._conv_report or ConversionReport()

    def group_usage(self, group):
        """Returns a list of the path where group is used in stage."""
        # We could build avail_groups_in_cmd, then filter in it
        # but that would not be optimal.
        # Hence the new visitor.
        res = []
        for cmd in self.commands:
            res += paths_using_group(cmd, group)
        return res

    def reset_validity(self):
        """Reset validity of all concepts in this stage and all its children."""
        for command in self.sorted_commands:
            command.reset_validity()
        for child in self.child_stages:
            child.reset_validity()
