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
Runner - base classes
---------------------

Implementation of the common classes for code_aster runners.

"""

import time

from ...common import (build_url, debug_message, debug_message2, info_message,
                       mount_enclosing_fs, translate)
from ..case import Case
from ..result import StateOptions as SO
from ..stage import Stage


class Runner:
    """
    Abstract class to define a runner.

    Args:
        case (Case): Case object to run.
        logger (optional[function]): Callback function used to send
            information messages.
        unittest (bool): Enable unittest mode.

    Attributes:
        _case (Case): Case object to run.
        _results (list[Result]): Memory of the results that must be processed
            for this RunCase.
        _queue (list[Result]): List of results that are waiting, running
            or pausing to be processed.
        _interm (list[Result]): Stack of intermediate results to calculate.
        _logger (function): Callback for logging of server commands.
        _console (function): Callback for the console (jobs output).
    """

    def __init__(self, case, **kwargs):
        self._unittest = kwargs.get('unittest', False)
        self._case = case
        self._results = []
        self._queue = []
        self._interm = []
        self._logger = kwargs.get('logger', debug_message)
        self._console = kwargs.get('console', debug_message)

        for result in self._case.results():
            if result.state & SO.NotFinished:
                self._results.append(result)
        self._queue = self._results[:]
        self._last_refresh = 0.
        self._min_refresh = 3 if not self._unittest else 0.2
        self._elaps_refresh = self._min_refresh

    @property
    def current(self):
        """Holds the current processed result."""
        return self._queue[0] if self._queue else None

    @property
    def current_stage(self):
        """Holds the current processed stage."""
        return self._case.result_stage(self.current)

    @property
    def stages_stack(self):
        """Holds the stack of intermediate stages."""
        return [self._case.result_stage(res) for res in self._interm]

    def is_started(self):
        """Tell if at least one result has been submitted."""
        for i in self._queue:
            if i.state & SO.Waiting == 0:
                return True
        return len(self._queue) == 0

    def is_finished(self):
        """Tell if all results have been processed."""
        return len(self._queue) == 0

    def cancel_next(self):
        """Mark all stages following `current` as cancelled and
        empty the queue."""
        for i in self._queue[1:]:
            i.state = SO.Waiting
        self._queue = []

    def log(self, *args):
        """Log a message about the commands on server."""
        self._logger(*args)

    def console(self, *args, **kwargs):
        """Log a message to the console about the calculation."""
        self._console(*args, **kwargs)

    def cleanup(self):
        """Cleanup function, called when a RunCase is removed."""

    def check_parameters(self):
        """Check parameters before starting."""
        job_infos = self._case.job_infos
        # add default values (essentially for api usages or testcases)
        if not job_infos.is_defined("version"):
            job_infos.set("version", "stable")
        if not job_infos.is_defined("mode"):
            job_infos.set("mode", job_infos.Batch)
        if not job_infos.is_defined("memory"):
            job_infos.set("memory", 2048)
        if not job_infos.is_defined("time"):
            job_infos.set("time", "01:00:00")
        debug_message2("Parameters:", job_infos.asdict())

    def start(self):
        """Start the case calculation process."""
        self.check_parameters()
        self.log(translate('Runner',
                           'Run case "{0}" calculations process started')
                 .format(self._name(self._case)))
        self.start_next()

    def start_next(self):
        """Start calculation for next result."""
        if self.is_finished():
            self.log(translate('Runner',
                               'Run case "{0}" calculations process finished')
                     .format(self._name(self._case)))
        elif not self.intermediate_stage():
            self.start_current()
            self._interm = []

    def start_current(self):
        """Activate calculation simulation for next result."""
        raise NotImplementedError("must be sub-classed")

    def intermediate_stage(self):
        """Treat intermediate stage.

        Returns:
            bool: True if the current stage is an intermediate stage.
        """
        if self.current_stage.is_intermediate():
            stage = self.current_stage
            stagename = self._name(stage)
            self.log('Stage "{0}" is an intermediate stage and will be '
                     'executed with the next one.'.format(stagename))
            self._interm.append(self._queue.pop(0))
            self.start_next()
            return True
        return False

    def refresh(self):
        """Refresh state of all *not finished* results."""
        now = time.time()
        # '_last_refresh' is the date of the last refresh.
        # '_elaps_refresh' is the elapsed time for the last refresh.
        # wait at least 2x before a new refresh.
        if now - self._last_refresh < 2 * self._elaps_refresh:
            return
        info_message(
            translate('Runner', "Asking the server for the job state..."))
        self._last_refresh = now
        self.do_refresh()
        self._elaps_refresh = max(self._min_refresh, time.time() - now)

    def do_refresh(self):
        """Refresh state of all *not finished* results."""
        raise NotImplementedError("must be sub-classed")

    def stop_current(self):
        """Implementation of the core of 'stop' action.

        Returns:
            bool: The current calculation has been stopped successfully.
        """
        raise NotImplementedError("must be sub-classed")

    def stop(self):
        """Stop the case calculation process."""
        self.refresh()
        current = self.current
        if self.stop_current():
            current.state = SO.Error
            self.cancel_next()
            self.log(translate('Runner',
                               'Run case "{0}" calculations process stopped')
                     .format(self._name(self._case)))
        else:
            self.log(translate('Runner',
                               'Run case "{0}" is already stopped.')
                     .format(self._name(self._case)))

    def pause(self):
        """Pause the execution (optional)."""

    def resume(self):
        """Resume a paused process (optional)."""

    def result_state(self, result):
        """Gets a result state.

        Returns:
            StateOptions: Current state of `result`.
        """
        state = result.state
        if state & SO.Finished:
            return state
        # usually done by `start_next` but not in case of reload
        while self.current_stage and self.current_stage.is_intermediate():
            self._interm.append(self._queue.pop(0))
        # refresh current
        self.refresh()
        state = result.state
        debug_message2("State of", result, ":", SO.name(state))
        return state

    def _name(self, obj):
        """Convenient function to print the name of an object."""
        names = []
        if isinstance(obj, Stage):
            name = self._name(obj.parent_case)
            if name:
                names.append(name)
            names.append(obj.name)
        elif isinstance(obj, Case):
            names.append(obj.name)

        return ':'.join(names)


class ServerInfos:
    """Abstract class that provides informations of the servers."""

    def __init__(self, **kwargs):  # pragma pylint: disable=unused-argument
        self._servers = []
        self._refreshed = set()

    @property
    def available_servers(self):
        """Return the list of available servers."""
        return self._servers

    def server_username(self, server):
        """Return the username to be used on a server.

        Returns:
            str: Username.
        """
        raise NotImplementedError("must be sub-classed")

    def server_hostname(self, server):
        """Return the hostname of a server.

        Returns:
            str: Name/IP of the server, None if it is not found.
        """
        raise NotImplementedError("must be sub-classed")

    def server_by_host(self, hostname):
        """Return the server name as label that matches the hostname.

        Returns:
            str: Server name if found, None otherwise.
        """
        found = None
        for server in self.available_servers:
            if self.server_hostname(server) == hostname:
                found = server
                break
        return found

    def server_versions(self, server):
        """Give the list of available versions on `server`.

        Returns:
            dict: Dict providing the version number (as string) for each
            version ('stable': '14.4.0').
        """
        raise NotImplementedError("must be sub-classed")

    def server_modes(self, server):
        """Give the modes supported by `server`.

        Returns:
            list(str): List of modes (as text).
        """
        raise NotImplementedError("must be sub-classed")

    def exec_modes(self):
        """Give the modes supported for debugging.

        Returns:
            list(str): List of modes (as text).
        """
        raise NotImplementedError("must be sub-classed")

    def refresh_once(self, server, force=False):
        """Refresh the informations of a server, only once per session."""
        if force or server not in self._refreshed:
            if self.refresh_one(server):
                self._refreshed.add(server)

    def refresh_one(self, server): # pragma: pylint disable=unused-argument
        """Refresh the informations of a server.

        Arguments:
            server (str): Server name.

        Returns:
            bool: *True* if it succeeded, *False* otherwise.
        """
        # does nothing by default

    def mount_filesystem(self, sname):
        """Mounts the file system in Gnome Virtual file system.

        Note:
            SFTP protocol is used. Mounts the home.

        Arguments:
            sname (str): name of the server.
        """
        # covered by remote tests, test_engine_XXX_remote.py
        user = self.server_username(sname)
        host = self.server_hostname(sname)

        # mount home and scratch
        scratch_url = build_url(user, host, "scratch")
        mount_enclosing_fs(scratch_url)

        home_url = build_url(user, host, "home")
        mount_enclosing_fs(home_url)

    def debug_runner(self, dummy):
        """Only for debugging in simulator runner"""
