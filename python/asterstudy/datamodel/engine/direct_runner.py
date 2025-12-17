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
Direct runner
-------------

This module defines a runner that directly executes code_aster in interactive
mode.

"""

from __future__ import unicode_literals

import os.path as osp

from ...common import RunnerError, current_time, to_unicode, translate, valid_file_name
from ...common.remote_utils import local_exec
from ..job_informations import JobInfos
from ..result import StateOptions as SO
from .abstract_runner import Runner, ServerInfos
from .engine_utils import create_profil_for_current


class Direct(Runner):
    """Runner that directly calls asrun to synchronously execute local and
    interactive calculations.
    This runner should be used inside a job started by external applications.

    Arguments:
        case, logger: see
            :obj:`datamodel.engine.abstract_runner.Runner`.

    Attributes:
        _infos (object): AsRunInfos instance.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._infos = DirectInfos()

    def do_refresh(self):
        """Refresh state of currently processed (calculated) result."""
        if self.is_finished() or not self.is_started():
            return

    def start_current(self):
        """Activate calculation simulation for next result."""
        stage = self.current_stage
        stages = self.stages_stack + [stage]
        stagename = self._name(stage)
        name = valid_file_name(stagename)
        stagedir = stage.folder
        export = osp.join(stagedir, "export")
        self.log(translate("Runner", 'Starting "{0}"...').format(stagename))
        job_infos = self._case.job_infos
        job_infos.start_time = current_time()

        try:
            prof = create_profil_for_current(None, self._case, stages, name, self._infos)
        except RunnerError as exc:
            self.log("ERROR: {0}".format(exc.msg))
            self.stop()
            raise

        with open(export, "w") as fexp:
            fexp.write(prof.get_content())

        jret, out, err = local_exec("as_run " + export, ignore_errors=True)
        with open(osp.join(stagedir, "error"), "w", encoding="utf-8", errors="ignore") as ferr:
            ferr.write(err)
        with open(osp.join(stagedir, "output"), "w", encoding="utf-8", errors="ignore") as ferr:
            ferr.write(out)
        if jret != 0:
            msg = translate("Runner", 'Execution of "{0}" failed'.format(stagename))
            self.log(msg)
            self.log(to_unicode(out))
            self.current.state = SO.Error
            self._update_result()
        else:
            self.current.state = SO.Success
            job_infos.jobid = 0
            job_infos.name = name
            job_infos.end_time = current_time()
            self._update_result()

    def stop_current(self):
        """Stop the current calculation process."""
        return True

    def _update_result(self):
        """
        Assign calculation state to the first result and remove
        it from list. In successfull case begin simulation for next
        result or interrupt simulation otherwise.
        """
        stagename = self._name(self.current_stage)
        if self.current.state & SO.Error:
            self.log(
                translate("Runner", 'Stage "{0}" calculation failed. Interruption').format(
                    stagename
                )
            )
            self.cancel_next()
        else:
            self.log(translate("Runner", 'Stage "{0}" calculation succeeded').format(stagename))
            self._queue.pop(0)
            self.start_next()


class DirectInfos(ServerInfos):
    """Minimal implementation for localhost execution."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._servers = ["localhost"]

    def server_username(self, server):
        """Return the username to be used on a server.

        Returns:
            str: Username.
        """
        return ""

    def server_hostname(self, server):
        """Return the hostname of a server.

        Returns:
            str: Name/IP of the server, None if it is not found.
        """
        return "localhost"

    def server_versions(self, server):
        """Give the list of available versions on `server`.

        Returns:
            dict: Dict providing the version number (as string) for each
            version ('stable': '14.4.0').
        """
        return {}

    def server_modes(self, server):
        """Give the modes supported by `server`.

        Returns:
            list(str): List of modes (as text).
        """
        return [JobInfos.InteractiveText]

    def exec_modes(self):
        """Give the modes supported for debugging.

        Returns:
            list(str): List of modes (as text).
        """
        return []
