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
Simulator runner
----------------

This module defines a simulator for code_aster executions.

"""

import os.path as osp
import time
from random import randint

from ...common import (debug_message2, debug_mode, localhost_server, make_dirs,
                       write_file)
from ..job_informations import JobInfos
from ..result import Message, MsgLevel, MsgType
from ..result import StateOptions as SO
from ..result import extract_messages
from .abstract_runner import Runner, ServerInfos


class Simulator(Runner):
    """Simulator for testing purposes.

    Arguments:
        case, params, logger: see
            :obj:`datamodel.engine.abstract_runner.Runner`.

    Attributes:
        _params (dict): Parameters for calculation running.
        _forced (dict[Result: bool result state]): Used to force Success or
            Error results in debug mode (checkboxes added in GUI).
        _fstop (list[bool]): For debugging allows to make a stop fail.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self._params = {}
        self._forced = {}
        self._fstop = []

        self._tinit = None
        self._duration = None

    def check_parameters(self):
        """Check parameters before starting: does nothing for simulator"""

    def debug_runner(self, params):
        """Force states/results."""
        self._params = params
        # forced states in debug_mode
        calcstates = {}
        for stage, res in self._params.get('forced_states', {}).items():
            pcase = stage.parent_case
            assert pcase, "no parent case for {}".format(stage)
            calcstates[pcase.stages.index(stage)] = res

        for i in self._queue:
            stage = self._case.result_stage(i)
            index = stage.parent_case.stages.index(stage)
            if stage is not None and index in calcstates:
                self._forced[i] = calcstates[index]
        debug_message2("forced results:", self._forced)
        self._fstop = self._params.get('forced_stop', [])
        debug_message2("forced stops:", self._fstop)

    def do_refresh(self):
        """Refresh state of currently processed (calculated) result."""
        if self.is_finished() or not self.is_started():
            return
        tend = time.time()
        if self._tinit \
        and (self._duration is None or tend - self._tinit > self._duration):
            self.console("Here we will find the full output of the job!",
                         reset=True)
            self.current.add_messages(extract_messages("random"))
            # add a warning
            stage = self.current_stage
            if stage.is_graphical_mode() and not stage.is_empty():
                cmdid = stage[len(stage) // 2].uid
                self.current.add_messages(
                    Message(
                        MsgLevel.Warn,
                        "This command emitted a warning message when "
                        "executing by the Simulator", MsgType.Command, cmdid,
                        0, 0))
            self._update_result()
            # refresh next if any
            self.refresh()
        else:
            self.console("The job is running: {}".format(
                time.strftime("%H:%M:%S")))

    def stop_current(self):
        """Stop the current calculation process."""
        assert self.current.state & SO.Running, self.current.state
        return True if not self._fstop else self._fstop.pop(0)

    def pause(self):
        """Pause the execution (optional)."""
        self.refresh()
        current = self.current
        if current and current.state & SO.Running:
            current.state = SO.Pausing

            self.log('Run case "{0}" calculations process paused'.format(
                self._name(self._case)))

    def resume(self):
        """Resume a paused process (optional)."""
        self.refresh()
        if not self.is_finished():
            self.current.state = SO.Running

            self.log('Run case "{0}" calculations process resumed'.format(
                self._name(self._case)))

    def start_current(self):
        """Activate calculation simulation for next result."""
        self.current.state = SO.Running
        job_infos = self._case.job_infos
        job_infos.jobid = str(randint(1, 1000))
        self._tinit = time.time()
        self._duration = self._simulation_time()

        stagename = \
            self._name(self.current_stage)
        self.log('{0:3} intermediate stages ignored by the simulator'.format(
            len(self.stages_stack)))
        self.log('Stage "{0}" start calculation'.format(stagename))
        self.console("The job will take {0} s.".format(self._duration))

    def _update_result(self):
        """
        Assign calculation state to the first result and remove
        it from list. In successfull case begin simulation for next
        result or interrupt simulation otherwise.
        """
        stagename = self._name(self.current_stage)
        self.current.state = self._simulation_state(self.current)
        self._simulate_state(self.current_stage, self.current.state)
        if self.current.state & SO.Error:
            self.log('Stage "{0}" calculation failed. Interruption'.format(
                stagename))
            self.cancel_next()
        else:
            self.log('Stage "{0}" calculation succeeded'.format(stagename))
            self._queue.pop(0)
            self.start_next()

    def _simulation_time(self):
        """
        Returns the simulation calculation random time in msec.
        """
        delay = randint(3, 5) if not (debug_mode() or self._unittest) else 0.1
        self.log("Emulating a run for {0} s...".format(delay))
        return delay

    def _simulation_state(self, result):
        """Returns the simulation calculation result state:
        Success or Error."""
        state = SO.Success
        if result in self._forced:
            if not self._forced[result]:
                state = SO.Error
        else:
            num = randint(0, 7)
            state = SO.Error if num > 5 else SO.Success
        return state

    def _simulate_state(self, stage, state):  # pragma pylint: disable=no-self-use
        """Simulate state for given stage."""
        if stage is not None and stage.folder:
            if not stage.is_intermediate() and state & SO.Success:
                res_dir = osp.join(stage.folder, "base")
                make_dirs(res_dir)
                file_name = osp.join(res_dir, "glob.1")
                write_file(file_name, '')
                file_name = osp.join(res_dir, "pick.1")
                write_file(file_name, '')


class SimulatorInfos(ServerInfos):
    """Provides informations of the servers for the simulator."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._servers = [
            localhost_server(),
        ]

    @staticmethod
    def server_versions(server):
        """Give the list of available versions on a server.

        Returns:
            dict: Dict providing the version number (as string) for each
            version ('stable': '14.4.0').
        """
        return {'stable': '14.4.0', 'testing': '15.1.0'}

    def server_username(self, server):
        """Return the username to be used on a server.

        Returns:
            str: Username.
        """
        return ''

    def server_hostname(self, server):
        """Return the hostname of a server.

        Returns:
            str: Name/IP of the server, None if it is not found.
        """
        return localhost_server()

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
        return [JobInfos.ExecOptimText]
