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
File Descriptors
----------------

Implementation of the file descriptors management functionality.
"""


# The pragma below has to be removed after migration to Python 3 and
# suppression of above two lines.
# pragma pylint: disable=wrong-import-position,wrong-import-order

import copyreg
import os.path as osp
import types
import urllib.parse
from collections import defaultdict

from ..common import (copy_file, is_reference, external_file,
                      exists_remote, no_new_attributes, WritingToExistingFileError)
from .aster_syntax import is_unit_valid
from .command import ModifiesStageInstance as ModifiesInstance
from .command import Command
from .command.helper import used_units
from .general import FileAttr


def _pickle_method(method):
    """So that instance methods can support pickle."""

    # Uncomment below to extend to class methods
    #if method.im_self is None:
    #    return getattr, (method.im_class, method.im_func.func_name)
    #else:
    return getattr, (method.__self__, method.__func__.__name__)

# register a pickle method for methods
copyreg.pickle(types.MethodType, _pickle_method)

def _unit_generate_helper(udefault, umin, umax, ulist):
    """
    Helper to file2unit, generates new unit.

    Arguments:
       udefault (int): default logical unit.
       umin (int): lower bound for the generated unit.
       umax (int): upper bound for the generated unit.
       ulist (list): list of taken units, cannot be reused.
    """
    unit = None

    if udefault is not None and \
        udefault not in ulist:
        unit = udefault
    elif umin is not None:
        unit = umin
    else:
        unit = 1

    while unit in ulist or not is_unit_valid(unit):
        unit += 1
    if umax is not None and unit > umax:
        raise ValueError("No available file descriptors.")

    return unit

def _recursion(pars, chs, func, res, skip, *args):
    """
    Helper function to perform operation `func` recursively,
    on parent and children stages.

    Arguments:
        pars (list): parent *Stage* to explore.
        chs (list): list of children *Stage* to explore.
        func (function): operation to perform.
        res (list): *list* to populate recusively with results.
            For file search operations, may also be an *int*.
        skip (bool): discard results from the first iteration.
            Used to explore parent and child, but not the stage itself.
        args (list): any arguments to pass to `func`.
    """
    npars, nchs = [], []
    if skip:
        save = res[:] if isinstance(res, list) else res
    for par in pars:
        res = func(par, res, *args)
        if par.parent_stage is not None:
            npars = [par.parent_stage]
    for child in chs:
        res = func(child, res, *args)
        # do not duplicate stages!
        for sub in child.child_stages:
            if sub not in nchs:
                nchs.append(sub)
    if skip:
        res = save
    if npars or nchs:
        res = _recursion(npars, nchs, func, res, False, *args)
    return res


class Info:
    "Keeps all Handle related information"

    _filename = _command2attrs = _imposed_attr = _embedded = None
    calling = None
    __setattr__ = no_new_attributes(object.__setattr__)

    def __init__(self, stage):
        self._filename = None
        self._command2attrs = defaultdict(set)
        self._imposed_attr = FileAttr.No
        self._embedded = False
        self.calling = stage

    def __mul__(self, other):
        """Support native Python '*' operator protocol."""
        assert self.filename == other.filename

        assert self.attr == other.attr

        assert self.embedded == other.embedded

    def copy_from(self, other):
        """Copy values from another object."""
        self._filename = other.filename
        # keep values of _command2attrs?
        self._imposed_attr = other.attr
        self._embedded = other.embedded

    @property
    def model(self):
        """History object to which this one is related"""
        return self.calling.model

    def autocopy(self):
        """Triggers autocopy of the associated stage"""
        return self.calling.autocopy()

    @property
    def filename(self):
        "Returns file name for the given handle."
        return self._filename

    @filename.setter
    @ModifiesInstance(True)
    def filename(self, filename):
        "Sets file name for the given handle."
        self._filename = filename

    @property
    def attr(self):
        "Returns cumulative FileAttr value for the given handle."
        if not self._command2attrs:
            return self._imposed_attr

        result = FileAttr.No
        for attrs in self._command2attrs.values():
            for attr in attrs:
                result |= attr

        return result

    @attr.setter
    @ModifiesInstance(True)
    def attr(self, value):
        """Sets user's FileAttr value for the given handle."""
        self._imposed_attr = value

    @property
    def first_attr(self):
        """Returns cumulative FileAttr value as its first definition."""
        # text stage
        if self.calling.is_text_mode(): # pylint: disable=no-member
            return self.attr

        # graphical stage
        filt = filter(lambda cmd: cmd in self,
                      self.calling.sorted_commands) # pylint: disable=no-member
        result = FileAttr.No
        try:
            cmd = next(filt)
            for attr in self[cmd]:
                result |= attr
        except StopIteration:
            pass
        return result

    @property
    def embedded(self):
        """Returns embedded state of the file."""
        return self._embedded

    @embedded.setter
    @ModifiesInstance(True)
    def embedded(self, value):
        """Sets embedded status for the file"""
        self._embedded = value

    @property
    def isreference(self):
        """
        Returns *True* if file is a reference to SALOME study object.
        """
        return is_reference(self.filename)

    @property
    def exists(self):
        """Returns file name presence in file system."""
        exists = False
        if self.filename:
            if self.isreference:
                sobj_name = external_file(self.filename)
                exists = sobj_name is not None
            elif self.isremote:
                exists = exists_remote(self.filename)
            else:
                exists = osp.isfile(self.filename)
        return exists

    @property
    def must_exist(self):
        """Tells if it must exist before starting a calculation."""
        return self.first_attr == FileAttr.In

    @property
    def commands(self):
        """Get commands which refer to the file"""
        return sorted(self._command2attrs.keys())

    def clear(self):
        """
        Clear the info: removes all registered commands.
        """
        self._imposed_attr = self.attr
        self._command2attrs.clear()

    def __contains__(self, given):
        """
        Support native Python "in" operator protocol.
        Checks the presence of command in command2attrs dict.

        Arguments:
            given (Command): Command being checked.

        Returns:
            bool: *True* if Command is contained in the dict;
            *False* otherwise.
        """
        return given in self._command2attrs

    def __getitem__(self, cmd):
        """
        Support native Python '[]' operator protocol.

        Arguments:
            cmd (Command): Key command object.

        Returns:
            attr for given command.
        """
        if isinstance(cmd, Command):
            return list(self._command2attrs[cmd])
        raise TypeError("Invalid argument type.")

    @ModifiesInstance(True)
    def __setitem__(self, cmd, attr):
        """
        Support native Python '[]' operator protocol.

        Arguments:
            cmd (Command): Key command object.
            attr (int): File attribute.
        """
        if isinstance(cmd, Command):
            self._command2attrs[cmd].add(attr)
            self._imposed_attr = self.attr
        else:
            raise TypeError("Invalid argument type.")

    @ModifiesInstance(True)
    def __delitem__(self, cmd):
        """
        Support native Python '[]' operator protocol.

        Arguments:
            cmd (Command): Key command object.
        """
        if isinstance(cmd, Command):
            del self._command2attrs[cmd]
        else:
            raise TypeError("Invalid argument type.")

    def __len__(self):
        """
        Support native Python 'len' operator protocol.

        Returns:
            int: Number of registered commands in info.
        """
        return len(self._command2attrs)

    def is_repeated(self, stage):
        """
        Test wether the file appears in another stage.

        Arguments:
            stage (Mixing) : stage the info objects belongs to.
        """
        return stage.other_unit_search(self.filename) is not None

    @property
    def server(self):
        """Host of the file (*None* if local)."""
        if (not self.filename) or self.isreference:
            return None
        return urllib.parse.urlsplit(self.filename).hostname

    @property
    def isremote(self):
        """Returns *True* if file hosted on remote server."""
        return self.server is not None

    @property
    def relpath(self):
        """Path relative to server."""
        return urllib.parse.urlsplit(self.filename).path

class Mixing:
    """Encapsulates file descriptors management functionality"""
    # pragma pylint: disable=no-member

    _handle2info = None
    __setattr__ = no_new_attributes(object.__setattr__)

    def __init__(self):
        """
        Create Case.

        Arguments:
            name (str): Name of the Case.
        """
        self._handle2info = defaultdict(self.fact_info)

    def fact_info(self):
        """Workaround to have a pickable object."""

        return Info(self)

    def __mul__(self, other):
        """Support native Python '*' operator protocol."""
        lhandle2info = self.handle2info
        rhandle2info = other.handle2info

        assert set(lhandle2info) ^ set(rhandle2info) == set()

        for handle, linfo in lhandle2info.items():
            rinfo = rhandle2info[handle]
            assert linfo * rinfo is None

    @property
    def handle2info(self):
        """dict[int/str, info]: returns `unite` to `keyword` mapping."""
        return self._handle2info

    def handle2file(self, unit):
        """
        Returns file name for the given unit.

        Arguments:
            unit (int/str): Unit identifier or basename of file.

        Returns:
            str: File name.
        """
        if unit not in self._handle2info:
            return None

        return self._handle2info[unit].filename

    def file2unit(self, filename, udefault=None, umin=None, umax=None,
                  ulist=None):
        """
        Generates unique unite for the given filename.

        Arguments:
            filename (str): File name.
            udefault (int): default logical unit.
            umin (int): lower bound for the generated unit.
            umax (int): upper bound for the generated unit.
            ulist (list): list of taken units, cannot be reused.

        Returns:
            int/str: Unique (for this case) unit identifier.

        Note:
            To avoid conflicts between stages, files
            for parent and child stages are checked.
        """
        unit = self.unit_search(filename)
        if unit is not None:
            return unit
        unit = self.unit_generate(udefault, umin, umax, ulist or [])
        return unit

    def unit_search(self, filename):
        """
        Recursive search for a logical unit, in the current stage,
        its parents and children.

        Arguments:
            filename (str): full path of the file.

        Returns:
            int/str: logical unit of the file if found, *None* otherwise.
        """
        return _recursion([self],
                          [self],
                          Mixing.stage_unit_search,
                          None,
                          False,
                          filename)

    def other_unit_search(self, filename):
        """
        Recursive search for a file in parent and child stages,
        but not the stage itself.

        Arguments:
            filename (str): full path of the file.

        Returns:
            int/str: logical unit of the file if found, *None* otherwise.
        """
        return _recursion([self],
                          [self],
                          Mixing.stage_unit_search,
                          None,
                          True,
                          filename)

    def unit_conflict(self, unit, filename):
        """
        Recursive search for a unit conflict,
        i.e. two files sharing the same unit.

        Arguments:
            unit (int/str): logical unit to test.
            filename (str): full file path to test.

        Returns:
            bool: *True* if there is no conflict, *False* otherwise.
        """
        blist = _recursion([self],
                           [self],
                           Mixing._unit_conflict,
                           [], True,
                           unit, filename)
        return all(blist)

    def file_conflict(self, unit, filename):
        """
        Recursive search for a file conflict,
        i.e. two units sharing the same file.

        Arguments:
            unit (int/str): logical unit to test.
            filename (str): full file path to test.

        Returns:
            bool: *True* if there is no conflict, *False* otherwise.
        """
        res = self.other_unit_search(filename)
        return (res in (None, unit), res in (unit,))

    def unit_generate(self, udefault, umin, umax, ulist):
        """
        Recursive generation of a logical unit.

        Arguments:
            udefault (int): default logical unit.
            umin (int): lower bound for the generated unit.
            umax (int): upper bound for the generated unit.
            ulist (list): list of taken units, cannot be reused.

        Note:
            Gets all taken units in parent and child stages
            to avoid conflicts.
        """
        uexcl = _recursion([self], [self], Mixing._taken_units, [], False)
        uexcl.extend(ulist)
        return _unit_generate_helper(udefault, umin, umax, uexcl)

    def stage_unit_search(self, unit, filename, callback=lambda x, y: x == y):
        """
        Search for a file name among existing entries.

        Arguments:
            unit (int/str): value to return if `filename` is not found.
            filename (str): file name to search for.
        """
        for handle, info in self._handle2info.items():
            if callback(info.filename, filename):
                unit = handle
                break
        return unit

    def basename2unit(self, basename):
        """
        Search for a file with given basename.
        Returns its unit if found, else -1.
        """
        # covered by remote tests
        return self.stage_unit_search(-1,
                                      basename,
                                      lambda x, y: osp.basename(x) == y)

    def _taken_units(self, ulist):
        """
        Appends the logical units used in the current stage to `ulist`.
        """
        return list(set(ulist) | set(self._handle2info.keys()))

    def _taken_info(self, ilist, unit):
        """
        Appends the info assigned to `unit` in the current stage to `ilist`.
        """
        if unit in self._handle2info:
            ilist.append(self._handle2info[unit])
        return ilist

    def other_info_search(self, unit):
        """Recursive search for `Info` objects associated to this `unit`
        in other stages.

        Arguments:
            unit (int): Unit number to be searched.

        Returns:
            list[*Info*]: List of `Info` objects used is other stages.
        """
        return _recursion([self], [self], Mixing._taken_info, [], True, unit)

    def _unit_conflict(self, blist, unit, fname):
        """
        Looks for a unit conflict in the current stage,
        i.e. two different files sharing the same unit.

        Arguments:
            blist (list<bool>): list where to append the result.
            unit (int/str): logical unit to test.
            fname (str): full path of the file to test.
        """
        blist.append(self.handle2file(unit) in (fname, None))
        return blist

    def ext2emb(self, filepath):
        """
        Generate a name for the embedded file.

        Arguments:
            filepath (str): file path when it used to be external.

        Returns:
            str: generated embedded file path.

        Note:
            Does not modify the data model.
        """
        return osp.join(self.model.tmpdir, osp.basename(filepath)) # pragma pylint: disable=no-member


    def parent_info(self, info):
        """
        Returns nearest similar file entry in parent stages, if any.

        Arguments:
            info (datamodel.file_descriptors.Info): File entry (Info object) to look for.

        Returns:
            datamodel.file_descriptors.Info: nearest *Info* object
            in parent stages with the same id.

        Note:
            Two *Info* objects are considered similar when they have
            the same basename.
        """
        res = None
        case = self.parent_case # pragma pylint: disable=no-member
        stlist = case[:self] # pragma pylint: disable=invalid-slice-index
        for stage in stlist:
            for inf in stage.handle2info.values():
                if inf.filename is not None and info.filename is not None:
                    if osp.basename(inf.filename) == osp.basename(info.filename):
                        res = inf
                        break
        return res


    def child_info_out(self, info):
        """
        Returns nearest similar file entry in child stages, if any.

        Arguments:
            info (datamodel.file_descriptors.Info): File entry (Info object) to look for.

        Returns:
            datamodel.file_descriptors.Info: nearest *Info* object
            in child stages with the same id.

        Note:
            Two *Info* objects are considered similar when they have
            the same basename.
        """
        case = self.parent_case # pragma pylint: disable=no-member
        stlist = [st for st in case if st.number > self.number] # pragma pylint: disable=no-member
        for stage in stlist:
            for inf in stage.handle2info.values():
                if inf.filename is not None and \
                   osp.basename(inf.filename) == \
                   osp.basename(info.filename) \
                   and inf.attr & FileAttr.Out:
                    return inf
        return None

    def copy2tmpdir(self):
        """
        When a stage is automatically copied
        copies the embedded files to the temp dir.
        """
        for info in self.handle2info.values():
            if info.embedded:
                source = info.filename
                bname = osp.basename(info.filename)
                dest = osp.join(self.model.tmpdir, bname) # pragma pylint: disable=no-member
                if source != dest:
                    copy_file(source, dest)
                info.filename = dest

    def basename_conflict(self, filename):
        """
        Looks for a basename conflict, i.e. a file with the same
        basename in the current stage.

        Arguments:
            filename (str): file path.

        Note:
            Due to Salome launcher not supporting two files with
            the same basename, we have to forbide it for two files
            of the same stage.
        """
        for info in self.handle2info.values():
            if filename and info.filename and \
               osp.basename(info.filename) == osp.basename(filename):
                return True
        return False

    def check_reused_out_file_in_cmd(self, current_cmd):
        """
        Looks for a file in the command that is being written ("out" file)
        after having been used a first time elsewere. This will almost always
        be misleading and lead to data losses or unexploitable files.

        Arguments:
            current_cmd (Command): command to explore.

        Raises:
            WritingToExistingFileError: if such a situation is detected
        """
        for unit in used_units(current_cmd):
            self._check_reused_out_file(unit, current_cmd)

    def check_reused_out_file(self, filename):
        """
        Test whether file `filename` is written after used a first time.
        Looks first in stage, then out of stage

        Arguments:
           filename (int or str): file name or identifier in Asterstudy
           current_cmd (Command): command

        Raises:
            WritingToExistingFileError: if such a situation is detected
        """
        unit = filename if isinstance(filename, int) else self._find_unit_from_filename(filename)
        if unit is None:
            return
        try:
            current_cmd = next(iter(self.handle2info[unit].commands)) \
                if self.is_graphical_mode() else None # pragma pylint: disable=no-member
            self._check_reused_out_file(unit, current_cmd)
        except StopIteration:
            pass

    def _find_unit_from_filename(self, filename):
        """Find unit in this stage, preceding and following ones from filename"""
        case = self.parent_case # pragma pylint: disable=no-member
        for stage in case:
            try:
                return next(k for k, v in stage.handle2info.items() if v.filename == filename)
            except StopIteration:
                continue
        return None

    def _check_reused_out_file(self, unit, current_cmd=None):
        """
        Test whether file `unit` is written after used a first time.
        Looks first in stage, then out of stage

        Arguments:
           unit (int): file identifier in Asterstudy (Fortran logical unit)
           current_cmd (Command): command, necessary for a graphical stage,
              unnecessary for a text stage

        Raises:
            WritingToExistingFileError: if such a situation is detected
        """
        info = self.handle2info.get(unit, None)

        # --- In stage (graphical)
        if info is not None and self.is_graphical_mode(): # pragma pylint: disable=no-member
            for cmd in info.commands:
                # If it is out, check previous use of the file
                if FileAttr.Out in info[current_cmd] and \
                   self.sorted_commands.index(cmd) < self.sorted_commands.index(current_cmd): # pragma pylint: disable=no-member
                    raise WritingToExistingFileError(info.filename)

                # Check further "out" use of the file
                if FileAttr.Out in info[cmd] and \
                   self.sorted_commands.index(cmd) > self.sorted_commands.index(current_cmd): # pragma pylint: disable=no-member
                    raise WritingToExistingFileError(info.filename)

        # --- Out of stage
        if info is not None:
            # If it is out, check previous use of the file
            if info.attr & FileAttr.Out and self.parent_info(info) is not None:
                raise WritingToExistingFileError(info.filename)

            # Check further "out" use of the file
            if self.child_info_out(info) is not None:
                raise WritingToExistingFileError(info.filename)

    def track_unused(self):
        """
        Track unused files (*Info* objects) and delete them.
        """
        for unit, info in self.handle2info.copy().items():
            if info is None or not info:
                del self.handle2info[unit]

    def text_filedesc(self):
        """
        Operations to files when switching to text mode.
        """
        self.track_unused()
        for handle in self.handle2info.values():
            handle.clear()

    def has_remote_files(self):
        """
        Returns *True* if remote files are present.
        """
        return any(info.isremote for info in self.handle2info.values())
