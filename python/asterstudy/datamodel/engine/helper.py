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
Engine helper functions
-----------------------

Implementation of helper functions for executions.

"""


import time
from math import exp

from ...common import hms2s, no_new_attributes
from .. import FileAttr
from ..result import StateOptions as SO
from . import runner_factory


class CalcWatcher:
    """Object to execute and watch for the completion of a *RunCase*.

    Create the object from a *RunCase* and its execution parameters::

        watch = CalcWatcher()
        watch.run_case = run_case

    Execute the *RunCase* synchronously::

        watch.run()

    or start it asynchronously and follow its state::

        watch.start()
        while not watch.is_finished():
            pass

    Check the state::

        assert watch.state & StateOptions.Success
        print(watch.state_name)

    Arguments:
        run_case (*RunCase*): *RunCase* object to be executed.
        parameters (dict): Dict of the execution parameters.
    """

    _rcase = _timeout = _state = _log = _engine = None
    _runner = _t_init = _t_refr = None

    __setattr__ = no_new_attributes(object.__setattr__)

    def __init__(self):
        """Initialization."""
        self._rcase = None
        self._timeout = None
        self._t_init = 1.e20
        self._t_refr = None
        self._state = SO.Waiting
        self._log = lambda _: None
        self._engine = None

    @property
    def run_case(self):
        """Attribute that holds the *RunCase*."""
        return self._rcase

    @run_case.setter
    def run_case(self, run_case):
        self._rcase = run_case

    def set_logger(self, logfunc):
        """Register a logger function.

        Arguments:
            logfunc (function): Logger function (*logfunc(str)*).
        """
        self._log = logfunc

    @property
    def log(self):
        """Logging function."""
        return self._log

    @staticmethod
    def tlimit2tout(time_limit):
        """Time limit to timeout."""
        return hms2s(time_limit) * 5

    @property
    def timeout(self):
        """Attribute that *holds* the timeout (in seconds).

        If it is not explicitly set, the timeout is equal to *time* (from
        parameters) multiplied by 5.
        """
        if self._timeout is None and self._rcase:
            return self.tlimit2tout(self._rcase.job_infos.get('time'))
        return self._timeout

    @timeout.setter
    def timeout(self, value):
        """Setter for the timeout.

        Arguments:
            value (str): Time out in seconds, MM:SS or in HH:MM:SS format.
        """
        self._timeout = hms2s(value)

    def _refresh_state(self):
        """Refresh the job state (but not to often!)."""
        if self._rcase and self._do_refresh():
            last = self._rcase.results()[-1]
            self._state = self._runner.result_state(last)
            self._t_refr = time.time()
            self._log("State is: {0}".format(SO.name(self._state)))

    @property
    def state(self):
        """Attribute that *holds* the current state of the execution.

        Note: A minimal delay is imposed between updates of the state.

        Returns:
            *StateOptions*: State of the execution encoded in a bitwise integer.
        """
        self._refresh_state()
        return self._state

    @property
    def state_name(self):
        """Attribute that *holds* the label of the state of the execution."""
        return SO.name(self.state)

    def start(self):
        """Start the calculation asynchronously."""
        self._state = SO.Waiting

        self._runner = runner_factory(case=self._rcase, engine=self._engine)
        self._runner.start()
        self._t_init = time.time()

    def is_finished(self):
        """Tell if the calculation is finished or if its time out expired.

        Returns:
            bool: *True* if the calculation ended or expired, *False* otherwise.
        """
        if self._runner is None:
            return False

        elapsed = time.time() - self._t_init
        if elapsed > self.timeout:
            self._log("Timeout reached ({0} s)".format(self.timeout))
            return True

        self._refresh_state()
        return self._runner.is_finished()

    def is_successful(self):
        """Tell if the calculation ended successfully.

        Returns:
            bool: *True* if the calculation ended with *Success* state,
            *False* if it ended with *Error* (fatal error) or *Interrupted*
            ('<S>' error) states.
        """
        return self.state & SO.Success != 0

    def run(self):
        """Execute the calculation and wait until its completion."""
        self.start()

        # waiting for the end of the calculation
        while not self.is_finished():
            pass

    def logfiles(self):
        """Returns the list of pathnames of the logfiles.

        Returns:
            list[str]: Paths of the logfiles.
        """
        paths = []
        stages = self._rcase.stages if self._rcase else []
        for stgi in stages:
            out = stgi.output_file()
            if out:
                paths.append(out)
        return paths

    def results_paths(self):
        """Returns the list of pathnames of the results.

        Returns:
            list[str]: List of the path names.
        """
        paths = []
        stages = self._rcase.stages if self._rcase else []
        for stgi in stages:
            for _, fileinfo in stgi.handle2info.items():
                if fileinfo.attr & FileAttr.Out and fileinfo.exists:
                    paths.append(fileinfo.filename)
        return paths

    @property
    def database_path(self):
        """Attribute that holds the pathname of the database (created by the
        last stage). It may not exist if 'no_database' parameter has been used.

        Returns:
            str: Path name to the database.
        """
        stages = self._rcase.stages if self._rcase else []
        if stages:
            return stages[-1].database_path
        return None

    def _do_refresh(self):
        """Tell if the state has to be refreshed.

        The state has to be refreshed if it has never been checked, if the
        calculation is already ended or it wasn't recently refreshed.

        If the state has been recently refreshed, ``_do_refresh`` waits for
        0.5 second before returning.

        The minimal delay between refreshings grows exponentially up to
        *max(time/20, 30)* seconds (and at least one second), where *time*
        is the time limit provided in the parameters.

        If the calculation is already ended, it returns immediately.
        """
        if self._state & SO.Finished:
            return True

        now = time.time()
        elapsed = now - self._t_init
        tau = max([5., min([30., self.timeout / 5. / 20.])])
        delay = max([1., tau * (1. - exp(-elapsed / tau))])
        if self._t_refr is not None and now - self._t_refr < delay:
            time.sleep(0.5)
            return False

        return True

    def set_engine(self, engine):
        """Select the engine to be used (mainly for unittest).

        Arguments:
            engine (*Engine*): One of the available engines.
        """
        self._engine = engine
