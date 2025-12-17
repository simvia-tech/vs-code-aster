# -*- coding: utf-8 -*-

# Copyright 2016 - 2017 EDF R&D
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
**Backup utility**

In case of failure in SALOME, the study content is often lost.
This module backups at least the stages and the list of datafiles for the
current case.

The study is backup each time *Save* feature is called into the directory
``$HOME/.asterstudy/backup``.

*The previous backup is available in* ``$HOME/.asterstudy/backup.1``, *and*
``backup.2``... *up to* ``backup.10``.

A backup can be restored by importing ``backup.export`` through menu
*Operations/Import Case*.

"""

import os
import os.path as osp

from ..common import is_reference, make_dirs, never_fails, rotate_path
from .general import FileAttr


class BackupHistory:
    """Object to backup an History during serialization."""

    _path = _comm = _files = None

    def __init__(self, root=None, _unittest=False):
        """Initializations"""
        if int(os.getenv("ASTERSTUDY_WITHIN_TESTS", "0")) and not _unittest:
            return
        root = root or os.getenv("HOME", "")
        path = osp.join(root, ".asterstudy", "backup")
        self._path = "."
        self._init_path(path)
        self._comm = []
        self._files = []

    @never_fails
    def _init_path(self, path):
        """Initialize the root directory. Ensure it does not fail even if run
        concurrently on same paths."""
        # unset until initializing the root directory
        self._path = None
        if osp.exists(path):
            rotate_path(path, count=10)
        make_dirs(path)
        self._path = path

    @property
    def path(self):
        """str: Attribute that holds the path value."""
        return self._path

    @never_fails
    def save_stage(self, stage, text):
        """Save the text representation of a Stage."""
        if not self.path:
            return
        name = "{0.name}_{0.number}".format(stage)
        filename = name + '.comm'
        self._comm.append(filename)
        with open(osp.join(self.path, filename), 'w') as fobj:
            fobj.write(text)

    @never_fails
    def add_file(self, filename, unit, attr):
        """Save usage of a file."""
        if not self.path:
            return
        if not is_reference(filename):
            self._files.append([filename, unit, attr])

    @never_fails
    def end(self):
        """End of the backup."""
        if not self.path:
            return
        # write an export file
        lines = []
        fmt = "F comm {0} D 1"
        for name in self._comm:
            lines.append(fmt.format(name))
        fmt = "F libr {0} {2} {1}"
        for infos in self._files:
            attr = infos[2]
            infos[2] = ''
            if attr & FileAttr.In:
                infos[2] += 'D'
            if attr & FileAttr.Out:
                infos[2] += 'R'
            lines.append(fmt.format(*infos))
        lines.append('')
        with open(osp.join(self.path, "backup.export"), 'w') as fobj:
            fobj.write(os.linesep.join(lines))
