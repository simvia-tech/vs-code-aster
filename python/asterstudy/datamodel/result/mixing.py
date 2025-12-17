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
Result Mixings
--------------

Implementation of Mixing classes used for Result definition.

"""


import html
import os
import os.path as osp
import re
import shutil
import warnings
from glob import glob

from ...common import (ExistingSwapError, MissingStudyDirError,
                       StudyDirectoryError, bold, copy_file, div, href,
                       is_localhost, make_dirs, never_fails, no_new_attributes,
                       preformat, to_unicode, translate)
from ...common.remote_utils import remove_remote_dir
from ..abstract_data_model import add_parent, remove_parent
from ..general import FileAttr
from .execution import Result
from .message import extract_messages
from .utils import RunOptions, StateOptions


class CaseMixing:
    """Result related CaseMixing."""

    _folder = _description = _is_backup = _use_yacs = None
    __setattr__ = no_new_attributes(object.__setattr__)

    def __init__(self):
        """Initializer"""
        self._folder = ""
        self._description = ""
        self._is_backup = False
        self._use_yacs = False

    def __mul__(self, other):
        """Support native Python '*' operator protocol."""
        assert self.description == other.description

        assert self.is_backup == other.is_backup

    @property
    def description(self):
        """str: Attribute that holds the Case's description."""
        return self._description

    @description.setter
    def description(self, value):
        """Assign the Case description."""
        self._description = value

    @property
    def is_backup(self):
        """Returns the purpose of this case."""
        return self._is_backup

    @is_backup.setter
    def is_backup(self, value):
        """Defines the purpose of this case."""
        self._is_backup = value

    @property
    def use_yacs(self):
        """Tell if this case is run through a Yacs schema."""
        return self._use_yacs

    @use_yacs.setter
    def use_yacs(self, value):
        """Mark as run with a Yacs schema."""
        self._use_yacs = value

    def run_options(self, stage):
        """
        Get available options for run.

        Arguments:
            stage (Stage, int): Stage being checked.

        Returns:
            int: Available run options (*RunOptions*).

        Raises:
            IndexError: If `stage` does not belong to this Case.
        """
        if isinstance(stage, int):
            stage = self[stage] # pragma pylint: disable=unsubscriptable-object
        if stage not in self.stages: # pragma pylint: disable=no-member
            raise IndexError("stage does not belong to case")
        value = RunOptions.Skip | RunOptions.Execute
        if self.can_reuse(stage):
            value = value | RunOptions.Reuse
        return value

    def can_reuse(self, stage):
        """
        Check if Stage's result can be re-used.

        Arguments:
            stage (Stage, int): Stage being checked.

        Returns:
            bool: *True* if result can be re-used; *False* otherwise.

        Raises:
            IndexError: If `stage` does not belong to this Case.
        """
        res = False
        if isinstance(stage, int):
            stage = self[stage] # pragma pylint: disable=unsubscriptable-object
        if stage not in self.stages: # pragma pylint: disable=no-member
            raise IndexError("stage does not belong to case")
        next_idx = self.stages.index(stage) + 1 # pragma pylint: disable=no-member
        if stage.state & StateOptions.Success:
            # do not check if remote database exists
            res = True
            if not stage.result.has_remote:
                stgdir = stage.folder
                res = (bool(glob(osp.join(stgdir, "base*", "glob.1*"))) and
                       (bool(glob(osp.join(stgdir, "base*", "pick.code_aster.infos*"))) and
                        bool(glob(osp.join(stgdir, "base*", "pick.code_aster.objects*"))) and
                        bool(glob(osp.join(stgdir, "base*", "pick.code_aster.sha*")))) or
                       (bool(glob(osp.join(stgdir, "base*", "pick.1*")))))
        elif stage.is_intermediate() and next_idx < len(self.stages): # pragma pylint: disable=no-member
            res = self.can_reuse(next_idx)
        return res

    def copy_from(self, other):
        """
        Copy content of given case to this one.

        Arguments:
            other (Case): Other case.
        """
        if self.nb_stages > 0: # pragma pylint: disable=no-member
            self.detach(self.stages[0]) # pragma pylint: disable=no-member
        for stage in other.stages:
            self.add_stage(stage) # pragma pylint: disable=no-member

        # clean directory
        if self.model.tmpdir: # pragma pylint: disable=no-member
            rootdir, _, files = next(os.walk(self.model.tmpdir)) # pragma pylint: disable=no-member
            for myfile in files:
                os.remove(osp.join(rootdir, myfile))

    def run(self, state=StateOptions.Success, add_messages=False):
        """
        Run case in dummy mode.

        Note:
            This function is used for test purposes only.
        """
        for stage in self.stages: # pragma pylint: disable=no-member
            if not stage.is_intermediate():
                if not stage.state & state:
                    stage.state = state
                if add_messages:
                    messages = extract_messages("random")
                    stage.result.add_messages(messages)
                if state == StateOptions.Error:
                    break
        return self

    def before_remove(self):
        """Hook that is called before a Case removing starts."""
        model = self.model # pragma pylint: disable=no-member
        if model is not None and model.current_case is not None:
            if model.current_case is self:
                raise RuntimeError("current case cannot be removed")

            for stage in self.stages: # pragma pylint: disable=no-member
                if stage in model.current_case.stages:
                    if stage.parent_case is self:
                        stage.result.clear()

    def results(self):
        """Gets the chain of calculated results in case."""
        res_list = []
        for stage in self.stages: # pragma pylint: disable=no-member
            result = stage.result
            if result is not None:
                if result.stage == stage:
                    res_list.append(result)
        return res_list

    def result_stage(self, result):
        """Gets the stage in case according to the specified result."""
        res_stage = None
        for stage in self.stages: # pragma pylint: disable=no-member
            if stage.result == result:
                res_stage = stage
                break
        return res_stage

    def is_running(self):
        """Tell if the *RunCase* is running.

        Returns:
            bool: *True* if the *RunCase* is running, *False* otherwise.
        """
        res_list = self.results()
        return bool(res_list and res_list[-1].state & StateOptions.NotFinished)

    def is_remote(self):
        """Tell if the Case is run remotely.

        Returns:
            bool: *True* if the Case is run remotely.
        """
        return not is_localhost(self.job_infos.server)  # pragma pylint: disable=no-member

    def messages(self):
        """Return the messages of all stages of the case.

        Returns:
            list[Message]: List of messages.
        """
        msglist = []
        for stage in self.stages: # pragma pylint: disable=no-member
            if not stage.state & StateOptions.Finished:
                break

            if stage.parent_case is not self or stage.is_intermediate():
                continue

            messages = stage.result.messages
            if not messages:
                output = stage.output_file()
                if output:
                    with open(output, 'rb') as fileout:
                        text = to_unicode(fileout.read())
                        stage.result.add_messages(extract_messages(text))
                    messages = stage.result.messages
            msglist.extend(messages)

        return msglist

    def show_message(self, maxlines=50000):
        """Return the messages of each stage of the case.

        Arguments:
            maxlines (int): Parse only the last `maxlines` lines.

        Returns:
            str: Rich text of the messages.
        """
        # TODO: it's a job for a dedicated module!
        alltxt = []
        header = [div("summary"), bold(translate("Result", "Summary"))]
        rtxt = []
        for stage in self.stages: # pragma pylint: disable=no-member
            if not stage.state & StateOptions.Finished:
                break
            if stage.parent_case is not self:
                continue
            title = bold(translate("Result",
                                   "Output messages for stage {0}")
                         .format(stage.name))
            # link
            rtxt.append(div(stage.name))
            header.append(href(title, "#" + stage.name))
            if stage.is_intermediate():
                rtxt.append(translate("Result",
                                      "Execution grouped with the following "
                                      "stage."))
                continue
            rtxt.append(title + " - [" \
                        + href(translate("Result", "top"), '#summary') + " / "\
                        + href(translate("Result", "bottom"), "#bottom") + "]")
            # show message file content
            mess = stage.output_file(prefer_message=True)
            if mess:
                with open(mess, 'rb') as fobj:
                    text = fobj.read().decode('utf-8', 'ignore')
                    _lines = text.splitlines()
                    if len(_lines) > maxlines:
                        _lines = _lines[-maxlines:]
                        _lines.insert(0,
                                      translate("Result",
                                                "Show only the last {0} lines")
                                      .format(maxlines))
                        text = os.linesep.join(_lines)
                text = html.escape(text, quote=False)
                rtxt.append(preformat(text))
            else:
                rtxt.append(translate("Result",
                                      "Full job output should be available"
                                      " in the directory {0!r}.")
                            .format(osp.join(stage.folder, 'logs')))

        rtxt.extend([div("bottom") + href(translate("Result", "back to top"),
                                          "#summary")])
        if len(header) > 2:
            alltxt.extend(header)
        else:
            alltxt = [header[0]]
        alltxt.extend(rtxt)
        txt = "\n".join(alltxt).strip()
        return "<br />".join(txt.splitlines())

    @property
    def base_folder(self):
        """Get the basename of the Case folder.
        Should be used only by the serializer."""
        return self._folder

    @base_folder.setter
    def base_folder(self, value):
        """Set the basename of the Case folder.
        Should be used only by the serializer."""
        self._folder = value

    @property
    def folder(self):
        """str: Attribute that holds Case's folder path."""
        return self._folder_template(self.model.folder) # pragma pylint: disable=no-member

    @property
    def remote_folder(self):
        """str: Case's remote folder for database results."""
        return self._folder_template(self.model.remote_folder) # pragma pylint: disable=no-member

    def _folder_template(self, root):
        """
        Helper function to build the case's folder.

        Arguments:
            root (str): folder related to History object.
        """
        if not self._folder:
            self._folder = self.name # pragma pylint: disable=no-member
        return osp.join(root, self._folder) if root and self._folder else ""

    @property
    def has_remote(self):
        """bool: Tell if a Stage owned by this Case uses a remote database."""
        return True in [stg.result.has_remote for stg in self.stages # pragma pylint: disable=no-member
                        if self is stg.parent_case]

    def rename_folder(self):
        """Rename the folder of a *RunCase* using the current *Case* name."""
        old = self.folder
        if osp.isdir(old):
            self._folder = ''
            # '.folder' will reset '._folder' from '.name'
            os.rename(old, self.folder)

    def make_run_dir(self):
        """
        Handles the embedded files for a run case before it is submitted.
        """
        first = self.stages[self.first_exclusive()] # pragma pylint: disable=no-member
        for stage in self[first:]: # pragma pylint: disable=unsubscriptable-object
            self._make_run_dir_helper(stage)

    def _make_run_dir_helper(self, stage):
        """
        Copies embedded files to `self.folder` and change their paths
        accordingly in `stage`. Called before `stage` is run.

        Arguments:
            stage (Stage): stage whose embedded files are to be moved.
        """
        embfolder = osp.join(self.model.folder, self.name, 'Embedded') # pragma pylint: disable=no-member
        make_dirs(embfolder)
        for info in stage.handle2info.values():
            if info.embedded:
                tmpfile = info.filename
                curfile = osp.join(embfolder, osp.basename(tmpfile))
                infi = stage.parent_info(info)

                # if the file doesn't appear in a preceding stage
                if not infi:
                    source = tmpfile
                    dest = curfile

                # if the file appears in a preceding stage
                if infi:
                    parfile = infi.filename

                    # in file, point to the preceding folder, do not copy again
                    if info.attr == FileAttr.In:
                        dest = source = parfile

                    # out file, point to current folder, do not copy
                    if info.attr == FileAttr.Out:
                        source = dest = curfile

                    # inout file, copy the file from another location
                    if info.attr == FileAttr.InOut:
                        source = parfile
                        dest = curfile

                if dest != source:
                    copy_file(source, dest)
                info.filename = dest

    def delete_dir(self, keep_logs=False):
        """Deletes the directory associated with the case.

        Arguments:
            keep_logs (bool): By default all the content is deleted.
                If `keep_logs` is *True* the log files are not deleted.
        """
        res = False
        # without model there is no folder
        if not self.model: # pragma pylint: disable=no-member
            return None

        casedir = self.folder
        if casedir and osp.isdir(casedir):
            if not keep_logs:
                shutil.rmtree(casedir, ignore_errors=True)
            else:
                for stage in self.stages: # pragma pylint: disable=no-member
                    stgdir = stage.folder
                    if osp.exists(stgdir):
                        _, dirs, files = next(os.walk(stgdir))
                        for dirn in dirs:
                            if dirn not in ("logs", ):
                                shutil.rmtree(osp.join(stgdir, dirn),
                                              ignore_errors=True)
                        for fname in files:
                            if fname not in ("message", ):
                                os.remove(osp.join(stgdir, fname))
            remove_remote_dir(self)
            res = True

        return res


class HistoryMixing:
    """Result related HistoryMixing."""

    _folder = _remote_folder_base = _cases = _no_dir_loaded = None
    __setattr__ = no_new_attributes(object.__setattr__)

    def __init__(self):
        """Create object."""
        self._folder = None
        self._no_dir_loaded = False
        self._cases = []

    @staticmethod
    def listdir_exclude_emb(directory):
        """Lists a directory subdirs omitting "Embedded" entries and hidden
        subdirs (for example, failed execution of a parametric study).

        Arguments:
            directory (str): Directory path to walk in.

        Returns:
            list[str]: List of existing subdirectories.
        """
        root, subdirs, _ = next(os.walk(directory))
        assert osp.samefile(root, directory)
        return [s for s in subdirs if s != "Embedded" and not s.startswith(".")]

    @property
    def missing_root(self):
        """Returns *True* if the study dir should be considered missing.

        Note:
             This happens when history had no directory at load time
             and there are run cases; or when the path is not defined
             or does not exist."""
        return (not bool(self.folder)) \
            or (not osp.isdir(self.folder)) \
            or (self._no_dir_loaded and self.run_cases)

    @property
    def cases(self):
        """list[Case]: Attribute that holds all Cases."""
        return self._cases

    @property
    def current_case(self):
        """Case: Attribute that holds single *current* Case."""
        return self._cases[-1] if self.cases else None

    @property
    def run_cases(self):
        """list[Case]: Attribute that holds list of *run* Cases."""
        return [case for case in self._cases[:-1] if not case.is_backup]

    @property
    def backup_cases(self):
        """list[Case]: Attribute that holds list of *run* Cases."""
        return [case for case in self._cases[:-1] if case.is_backup]

    @property
    def folder(self):
        """str: Attribute that holds study related root directory."""
        return self._folder

    @folder.setter
    def folder(self, value):
        """
        Set study folder.

        Note:
            If `value` is an existing directory, this creates a
            subdirectory for embedded files for the current case.
        """
        if osp.basename(value) == "_Files":
            warnings.warn("\n    Path {0!r} seems invalid, probably due to "
                          "a known issue in SALOME Save()."
                          "\n    Study base folder is not changed."
                          .format(value), RuntimeWarning)
            return
        self._folder = value
        if (not self._folder) or (not osp.isdir(self._folder)):
            self._no_dir_loaded = True
        if self._folder:
            dirname = osp.join(self._folder, 'Embedded')
            make_dirs(dirname)

    @property
    def remote_folder(self):
        """str: remote folder (with the case suffix) on which result
        databases are kept."""
        # if 'folder' is not yet initialized
        if not self.folder or not self._remote_folder_base:
            return ""
        bname = osp.basename(osp.normpath(self.folder))
        return osp.join(self._remote_folder_base, bname)

    @property
    def remote_folder_base(self):
        """str: base remote folder (without the case suffix), as the user
        set it."""
        return self._remote_folder_base

    @remote_folder_base.setter
    def remote_folder_base(self, value):
        """
        Register the base remote folder on which remote databases will be kept.
        """
        self._remote_folder_base = value

    def new_run_case_name(self, prefix=""):
        """Returns an inexisting name for a Runcase, the folder must not
        exist too.

        Arguments:
            root (str): Root for the new case. If *None*, "Case" is used.

        Returns:
            str: Name based on *root* that doesn't yet exist in children.
        """
        class FakeNode:
            """Fake node to store existing path names."""
            def __init__(self, name):
                self.name = name

        fake = []
        for path in self.existing_run_case_names():
            fake.append(FakeNode(path))
        prefix = prefix or "RunCase"
        return self.new_name(prefix, fake) # pragma pylint: disable=no-member

    def existing_run_case_names(self):
        """Returns the list of existing RunCase names.

        Returns:
            list[str]: Existing RunCase names.
        """
        names = [i.name for i in self.run_cases]
        if self.folder:
            for path in glob(osp.join(self.folder, "RunCase*")):
                names.append(osp.basename(path))
        return names

    def _copy_case(self, root, name, backup=True):
        "Create backup Case"
        if not name:
            # pragma pylint: disable=no-member
            name = self.new_name(root, self.backup_cases + self.run_cases)

        ref_case = self.current_case
        case = ref_case.copy(name)
        case.is_backup = backup

        # it is like all stages were reused
        # so put current last
        for i in range(ref_case.nb_stages):
            # pragma pylint: disable=unsubscriptable-object
            plist = ref_case[i].parent_nodes
            plist.append(plist.pop(plist.index(ref_case)))

        return case

    def create_backup_case(self, name=None):
        "Create backup Case."
        return self._copy_case("BackupCase", name, backup=True)

    def create_parametric_case(self, name=None):
        """Create a parametric Case, showed as a RunCase but just a copy as a
        backup Case with a different name."""
        if not name:
            # pragma pylint: disable=no-member
            name = self.new_name("ParamCase",
                                 self.backup_cases + self.run_cases)
        param_case = self.create_run_case(name=name)
        param_case.use_yacs = True
        param_case.is_backup = False
        return param_case

    def create_run_case(self, exec_stages=None, reusable_stages=None,
                        name=None):
        """
        Create and initialize Run Case.

        The resulting Run case will contain Stages selected from Current
        case in accordance with below described rules.

        The stages to execute are specified via the *exec_stages*
        parameter. It can be:

        - Single integer value: in this case only Stage with specified
          index is executed.
        - List or tuple of two integer values: in this case all Stages
          in given range (inclusively) are executed.
        - List of tuple of one integer value: in this case all Stages
          starting from given one are executed.
        - None (default): all Stages are executed.

        Note:

        - All Stages preceeding first executed Stage are "re-used".
        - All Stages following last executed Stage are omitted.

        Arguments:
            exec_stages (Optional[multiple]): Indexes of stages to execute.
                Defaults to *None*.
            reusable_stages (Optional[multiple]): Indexes of executed stages
                that will be reusable. By default, only the last stage will be
                marked as reusable.
            name (str): Name for Run Case. Defaults to *None* (in this
                case the name is automatically assigned).

        Return:
            Case: New Run Case.

        Raises:
            IndexError: If given range of stages is invalid.
            RuntimeError: If stage aimed to be re-used, cannot be
                reused.
        """
        # pragma pylint: disable=unsubscriptable-object
        ref_case = self.current_case

        first_stage = 0
        last_stage = ref_case.nb_stages
        if isinstance(exec_stages, (list, tuple)):
            if exec_stages:
                first_stage = exec_stages[0]
                if len(exec_stages) > 1:
                    last_stage = exec_stages[1] + 1
        elif exec_stages is not None:
            first_stage = exec_stages
            last_stage = first_stage + 1

        if first_stage < 0 or first_stage >= ref_case.nb_stages or \
                last_stage < 0 or last_stage > ref_case.nb_stages or \
                last_stage <= first_stage:
            raise IndexError("wrong range of stages")

        if reusable_stages is None:
            reusable_stages = [last_stage - 1]
        elif not isinstance(reusable_stages, (list, tuple, range)):
            reusable_stages = [reusable_stages]

        if not name:
            name = self.new_run_case_name() # pragma pylint: disable=no-member

        # check results available for reuse
        for i in range(first_stage):
            ref_stage = ref_case[i]
            if not ref_stage.state & StateOptions.Success:
                raise RuntimeError("Cannot reuse stage '{0.name}'"
                                   .format(ref_stage))

        run_case = ref_case.copy(name)

        # reused stages: put current last
        for i in range(first_stage):
            plist = ref_case[i].parent_nodes
            plist.append(plist.pop(plist.index(ref_case)))

        # switch stages to be executed, as well as skipped stages
        for i in range(first_stage, ref_case.nb_stages):
            ref_stage = ref_case[i]
            if ref_stage.parent_case is ref_case:

                assert ref_stage.cases == [ref_case, run_case]
                # make run_case the new parent (move ref_case at last position)
                ref_stage.move_parent(ref_case)

        run_case.copy_shared_stages_from(first_stage + 1)

        # make current point to stages owned by run_case whenever possible
        for i in range(first_stage, ref_case.nb_stages):
            run_stage = run_case[i]

            # should be owned by run_case by now, reset folder
            assert run_stage.parent_case is run_case or i >= last_stage
            run_stage.base_folder = ""

            # point current to it
            old_stage = ref_case[i]
            assert old_stage.parent_case is not ref_case or i >= last_stage

            # if not the same, switch
            if old_stage is not run_stage:
                assert old_stage.parent_case is not run_case
                remove_parent(old_stage, ref_case)
                add_parent(run_stage, ref_case)

                # after modifying child relations, don't forget to reorder!
                ref_case.sort_children(type(run_stage), 'number')

            # mark as intermediate stage if needed
            if i not in reusable_stages:
                if i < last_stage - 1:
                    run_stage.set_intermediate()
                elif i == last_stage - 1:
                    run_stage.set_last_nodb()

        if last_stage < ref_case.nb_stages:
            run_case.detach(run_case[last_stage])

        # clear any result owned by current
        mylist = [st for st in ref_case.stages if st.parent_case is ref_case]
        for stage in mylist:
            stage.result.clear()

        return run_case

    def __mul__(self, other):
        """Support native Python '*' operator protocol."""
        assert self.folder == other.folder, (self.folder, other.folder)

    def hdf_name(self):
        """Return the HDF filename"""
        return re.sub("_Files$", "", self.folder) + ".hdf"

    @classmethod
    def warn(cls, hist):
        """
        Emit dedicated exceptions with quick hints to the user
        if the study directory is missing or incomplete.

        Arguments:
            hist (HistoryMixing): the history to inspect

        Note:
            The `folder` attribute (expected study directory)
            must have been set before to call this method.
        """
        def _missing_root(hist):
            """Task for a missing study directory."""
            if not hist.folder:
                msg = "The study directory is undefined."
                raise MissingStudyDirError(msg)

            msg = translate("AsterStudy",
                            "The study directory '{0}' did not exist "
                            "and had to be created empty."
                           ).format(hist.folder)
            msg += "\n\n"
            msg += translate("AsterStudy",
                             "If you moved the HDF study '{0}' from another "
                             "location, please make sure to move "
                             "the study directory as well.\n\n"
                             "Click 'Cancel', move the study directory "
                             "then try again "
                             "or click 'OK' to continue without study "
                             "directory."
                            ).format(hist.hdf_name())
            raise MissingStudyDirError(msg)

        def _missing_stage(hist, stage, _):
            """Task for each *Stage* without subfolder"""
            msg = translate("AsterStudy",
                            "The study directory '{0}' does not match "
                            "the HDF study '{1}'.\n"
                            "For instance, subdirectory '{2}' does not "
                            "exist."
                           ).format(hist.folder, hist.hdf_name(),
                                    stage.folder)
            msg += "\n\n"
            msg += translate("AsterStudy",
                             "If you moved the HDF study '{0}' from another "
                             "location, please make sure to move "
                             "the study directory as well.\n\n"
                             "Click 'Cancel', move the study directory "
                             "then try again "
                             "or click 'OK' to continue without study "
                             "directory."
                            ).format(hist.hdf_name())
            raise StudyDirectoryError(msg)

        def _missing_subdir(mydir):
            """Task for each subfolder without *Stage*"""
            msg = translate("AsterStudy",
                            "The study seems incomplete "
                            "with regard to the study directory.\n"
                            "For instance, subdirectory '{0}' has no "
                            "corresponding stage."
                           ).format(osp.abspath(mydir))
            raise StudyDirectoryError(msg)

        def _empty_case(case):
            """Task for a case with no owned stages"""
            msg = translate("AsterStudy",
                            "There seems to be empty cases in the study.\n\n"
                            "For instance, case {0} is empty.\n\n"
                            "Continuing will delete them."
                           ).format(case.name)
            raise StudyDirectoryError(msg)

        def _empty_casedir(hist, casedir):
            """Task for a case directory with no subdir"""
            msg = translate("AsterStudy",
                            "There seems to be empty cases directories in "
                            "the study.\n\n"
                            "For instance, directory '{0}' is empty.\n\n"
                            "Continuing will remove them."
                           ).format(osp.join(hist.folder, casedir))
            raise StudyDirectoryError(msg)

        hist.check_dir_template(_missing_root, _missing_stage, \
                                _missing_subdir, _empty_case, _empty_casedir)

    @classmethod
    def full_warn(cls, hist):
        """
        Emit dedicated exceptions with detailed info to the user
        if the study directory is missing or incomplete.

        Arguments:
            hist (HistoryMixing): the history to inspect

        Note:
            The `folder` attribute (expected study directory)
            must have been set before to call this method.
        """
        def _missing_root(_):
            """Task for a missing study directory."""
            msg = translate("AsterStudy",
                            "Run cases will not be loaded.")
            msg += "\n\n"
            msg += translate("AsterStudy", "Continue anyway?")
            raise StudyDirectoryError(msg)

        stnames, dirs, cnames, cdirs = hist.check_dir_template(_missing_root)

        if not stnames and not dirs and not cnames and not cdirs:
            return

        msg = ""
        if stnames:
            msg += translate("AsterStudy", "The following stages will not be "
                             "loaded ({0}/{1}):\n"
                            ).format(min(len(stnames), 5), len(stnames))
            for i in range(min(len(stnames), 5)):
                msg += "    {}\n".format(stnames[i])
            msg += "\n"
            destdir = osp.join(hist.folder, "not_loaded")
            msg += translate("AsterStudy",
                             "The commands files will be saved into "
                             "the directory {0}\n"
                            ).format(destdir)

        if dirs:
            msg += translate("AsterStudy", "The following subfolders will be "
                             "deleted ({0}/{1}):\n"
                            ).format(min(len(dirs), 5), len(dirs))
            for i in range(min(len(dirs), 5)):
                msg += "    {}\n".format(dirs[i])

        msg += "\n"
        msg += translate("AsterStudy", "Continue anyway?")
        raise StudyDirectoryError(msg)

    @classmethod
    def clean(cls, hist):
        """
        Makes the study directory consistent with the study:
        deletes stages without subfolder and conversely.

        Arguments:
            hist (HistoryMixing): the history to inspect

        Note:
            The `folder` attribute (expected study directory)
            must have been set before to call this method.
        """
        def _missing_root(hist):
            """Task for a missing study directory"""
            hist.current_case.copy_shared_stages_from(1)
            for case in hist.run_cases:
                case.delete()

        def _missing_stage(hist, stage, case):
            """Task for each *Stage* without subfolder"""
            destdir = osp.join(hist.folder, "not_loaded")
            backup_stage(destdir, stage)
            if not stage.is_intermediate():
                if stage in hist.current_case:
                    hist.current_case.copy_shared_stages_from(stage.number)
                stage.delete()
            else:
                case.detach(stage)

        def _missing_subdir(subdir):
            """Task for each subfolder without *Stage*"""
            shutil.rmtree(subdir)

        def _empty_case(case):
            """Task for a case with no owned stages"""
            case.delete()

        def _empty_casedir(hist, casedir):
            """Task for a case directory with no subdir"""
            os.rmdir(osp.join(hist.folder, casedir))

        hist.check_dir_template(_missing_root, _missing_stage, \
                                _missing_subdir, _empty_case, _empty_casedir)

    def check_dir_template(self,
                           missing_root=lambda _: None,
                           missing_stage=lambda *_: None,
                           missing_subdir=lambda _: None,
                           empty_case=lambda _: None,
                           empty_casedir=lambda *_: None):
        """
        Template for operations checking the study directory.

        Returns:
            tuple(stagedirs, orphandirs): List of paths.

            `stagedirs` is the list of the stage directories.

            `orphandirs` is the list of subdirectories of cases that are not a
            stage folder.
        """
        if self.missing_root:
            return missing_root(self)

        # list stage subdirectories
        dirlist = []
        stlist = []
        clist = []
        cdirlist = []
        casedirs = HistoryMixing.listdir_exclude_emb(self.folder)

        for casedir in casedirs:
            stdirs = HistoryMixing.listdir_exclude_emb(osp.join(self.folder,
                                                                casedir))
            for stdir in stdirs:
                dirlist.insert(0, osp.join(self.folder, casedir, stdir))

        # delete stage with no subdir
        for case in list(reversed(self.run_cases)):
            for stage in list(reversed(case.stages)):
                # Stage that may not have a directory:
                #     if no case directory, detach stage
                if not osp.isdir(case.folder) and stage.is_intermediate():
                    missing_stage(self, stage, case)

                # Stage that must have a directory:
                #     if no directory, deal with stage.
                elif not (osp.isdir(stage.folder) or stage.is_intermediate()):
                    stlist.append("{0}/{1}".format(stage.parent_case.name,
                                                   stage.name))
                    missing_stage(self, stage, case)
                else:
                    try:
                        dirlist.remove(stage.folder)
                    except ValueError:
                        pass

        # delete subdirs with no stage
        for orphandir in dirlist:
            missing_subdir(orphandir)

        # handle run cases with no owned stages
        for case in self.run_cases:
            if case.first_exclusive() == -1:
                clist.append(case.name)
                empty_case(case)

        # remove empty case directories
        casedirs = HistoryMixing.listdir_exclude_emb(self.folder)
        for casedir in casedirs:
            if not os.listdir(osp.join(self.folder, casedir)):
                cdirlist.append(osp.join(self.folder, casedir))
                empty_casedir(self, casedir)

        # return `dirlist` and `stagelist`
        return (stlist, dirlist, clist, cdirlist)

    @property
    def tmpdir(self):
        """
        Directory where embedded files are put for the current case.
        """
        if not self.folder:
            return None
        return osp.join(self.folder, 'Embedded')

    def clean_embedded_files(self):
        """Removes directory with embedded files."""
        tmpdir = self.tmpdir
        if tmpdir and osp.isdir(tmpdir):
            _, subdirs, _ = next(os.walk(tmpdir))
            assert not subdirs
            shutil.rmtree(tmpdir)

    def save_embedded_files(self, directory):
        """
        Handle embedded files at save time.

        Arguments:
            directory (str): directory where to copy embedded files.

        Returns:
            list<str> : a list with the basenames of emb files.
        """
        tmpdir = self.tmpdir
        emb = []
        if tmpdir and osp.isdir(tmpdir):
            _, _, bnames = next(os.walk(tmpdir))
            for bname in bnames:
                source = osp.join(tmpdir, bname)
                dest = osp.join(directory, bname)
                assert source != dest
                shutil.copyfile(source, dest)
            emb = bnames
        return emb

    def load_embedded_files(self, directory, files, check=True):
        """
        Handle embedded files at load time.

        Arguments:
            directory (str): directory where files are stored.
            files (list<str>): list of basenames.
            check (bool): if *True*, checks there are no embedded
                files in the study dir at load time.

        Raises:
            ExistingSwapError: if there are files
                in the study directory at load time.
        """
        # test that there are no embbedded files
        tmpdir = self.tmpdir
        if (not tmpdir) or (not osp.isdir(tmpdir)):
            return
        if os.listdir(tmpdir):
            if check:
                errmsg = translate("AsterStudy",
                                   "Existing embedded files have been detected"
                                   " in directory {0}.\n"
                                   "This could be due to Salome stopping "
                                   "unexpectedly.\n"
                                   "Loading will override them.\n"
                                   "Do you wish to continue?").format(tmpdir)
                raise ExistingSwapError(errmsg)

            self.clean_embedded_files()
            make_dirs(tmpdir)
        for bname in files:
            source = osp.join(directory, bname)
            dest = osp.join(tmpdir, bname)
            assert source != dest
            shutil.copyfile(source, dest)


class StageMixing:
    """Result related StageMixing."""

    _result = _last_nodb = None
    _folder = ""
    __setattr__ = no_new_attributes(object.__setattr__)

    def __init__(self):
        """Create object."""
        self._result = Result(self)
        self._folder = ""
        self._last_nodb = False

    @property
    def result(self):
        """Result: Attribute that holds Stage's result."""
        return self._result

    @result.setter
    def result(self, value):
        """Setter for the result."""
        self._result = value

    @property
    def state(self):
        """int: Attribute that holds Stage's Result status
        (*StateOptions*)."""
        return self.result.state

    @state.setter
    def state(self, state):
        """Set Stage's Result status (*StateOptions*)."""
        self.result.state = state

    def is_intermediate(self):
        """Tell if the stage is an intermediate one
        (means executed grouped with the following).
        """
        return self.result.is_intermediate()

    def set_intermediate(self):
        """Mark as an intermediate stage (not reusable)."""
        self.state = self.state | StateOptions.Intermediate

    def set_last_nodb(self):
        """Mark the last stage of a RunCase as not reusable (with no database,
        but it is not an intermediate stage)."""
        self._last_nodb = True

    def is_without_db(self):
        """Tell if the stage doesn't create a database.

        Returns:
            bool: *True* if this is the last stage and it doesn't create a
            database, or if it is an intermediate stage. *False* otherwise.
        """
        return self._last_nodb or self.is_intermediate()

    @property
    def folder(self):
        """str: Attribute that holds Stage's folder path."""
        return self._folder_template(self.parent_case.folder) # pragma pylint: disable=no-member

    @property
    def remote_folder(self):
        """str: Remote folder where Stage's result database are kept."""
        return self._folder_template(self.parent_case.remote_folder) # pragma pylint: disable=no-member

    def _folder_template(self, cfolder):
        """
        Helper method to build the Stage's folder.

        Arguments:
            cfolder (str): the parent Case's folder.
        """
        if not self._folder:
            self._folder = 'Result-' + self.name # pragma pylint: disable=no-member
        return osp.join(cfolder, self._folder)

    def output_file(self, prefer_message=False):
        """Return the first non-empty output files.
        This function should only be called after the execution.

        Arguments:
            prefer_message (bool): Select 'message' file first if *True*.
                Otherwise, preference goes to log files.

        Returns:
            str: Path to the output filename.
        """
        base = self.folder
        output = []
        output.extend(glob(osp.join(base, "logs", "[0-9]*_*Container_*.log")))
        output.extend(glob(osp.join(base, "logs", "output.log.*")))
        if prefer_message:
            output.insert(0, osp.join(base, "message"))
        else:
            output.append(osp.join(base, "message"))
        found = ""
        while output:
            path = output.pop(0)
            if osp.isfile(path) and os.stat(path).st_size != 0:
                found = path
                break
        return found

    def set_remote(self, value):
        """
        Sets the root remote folder if it is not already set,
        checks its consistence otherwise.

        Arguments:
            value (str): root remote folder.
        """
        # None means no remote directory
        if not value:
            return
        existing = self.model.remote_folder_base # pragma pylint: disable=no-member
        if not existing:
            self.model.remote_folder_base = value # pragma pylint: disable=no-member
        elif osp.normpath(existing) != osp.normpath(value):
            msg = ("The specified remote directory {0} is different "
                   "from the remote directory {1} of previous "
                   "runs".format(existing, value))
            raise StudyDirectoryError(msg)
        self.result.has_remote = True

    @property
    def database_path(self):
        """Return the pathname of the results database of the stage."""
        folder = self.remote_folder if self.result.has_remote else self.folder
        return osp.join(folder, 'base-stage{0}'.format(self.number)) # pragma pylint: disable=no-member

    @property
    def base_folder(self):
        """Get the basename of the Stage folder.
        Should be used only by the serializer."""
        return self._folder

    @base_folder.setter
    def base_folder(self, value):
        """Set the basename of the Stage folder.
        Should be used only by the serializer."""
        self._folder = value

    def __mul__(self, other):
        """Support native Python '*' operator protocol."""
        assert self.result * other.result is None

    def before_remove(self):
        """Prepare deletion."""
        self._result = None


@never_fails
def backup_stage(destdir, stage):
    """Backup the content of a Stage.

    Argumnents:
        destdir (str): Destination directory.
        stage (Stage): Stage to backup.
    """
    make_dirs(destdir)

    name = "{0}-{1}.comm".format(stage.parent_case.name, stage.name)
    with open(osp.join(destdir, name), "w") as fobj:
        fobj.write(stage.get_text())
