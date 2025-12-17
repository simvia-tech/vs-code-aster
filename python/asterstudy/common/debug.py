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
Debug
-----

Debugging functionality for AsterStudy application.

"""


import os
import pdb
import re
import sys



__all__ = ["debug", "profile_code"]


def init_sys_path():
    """Fill sys path with directories of debugged files."""
    regexp = re.compile(r".*\.py$")
    for rootdir, _, files in os.walk(sys.path[0]):
        matched = [filename for filename in files if regexp.match(filename)]
        if matched:
            sys.path.append(rootdir)


def debug():
    """Run debugger."""
    init_sys_path()
    pdb.set_trace()


def profile_code(cmd, locs, filename=None):
    """
    Profile code.

    Command to profile is given in the same syntax as accepted by *exec*
    operator.

    If *filename* is specified, profiler statistics is printed to the
    file; otherwise it is printed to stdout.

    Example of usage.

    Arguments:
        cmd (str): A command to profile.
        locs (dict): Locals to use
    """
    import profile
    profiler = profile.Profile()
    profiler.runctx(cmd, globals(), locs)

    import pstats
    stat = pstats.Stats(profiler)

    if filename is not None:
        stat.strip_dirs().sort_stats('cumulative').dump_stats(filename)
    else:
        stat.strip_dirs().sort_stats('cumulative').print_stats()
