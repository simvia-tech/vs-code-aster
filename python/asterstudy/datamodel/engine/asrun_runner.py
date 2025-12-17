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
AsRun runner
------------

This module defines a runner using ``as_run`` for code_aster executions.

"""


import getpass

from ...common import (LogFiles, RunnerError, Singleton, current_time,
                       debug_message2, debug_mode, ping, to_unicode, translate,
                       valid_file_name)
from ..result import StateOptions as SO
from ..job_informations import JobInfos
from ..result import extract_messages
from .abstract_runner import Runner, ServerInfos
from .engine_utils import (convert_asrun_state, create_profil_for_current,
                           need_asrun, text_to_asrun)

class AsRun(Runner):
    """Runner that use asrun backend.

    Arguments:
        case, logger: see
            :obj:`datamodel.engine.abstract_runner.Runner`.

    Attributes:
        _run (object): AsterRun instance.
        _infos (object): AsRunInfos instance.
        _hdlr (object): AsterCalcHandler instance.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._run = AsRunInfos.asrun_instance(**kwargs)
        self._infos = AsRunInfos()
        self._infos.set_log_callback(self._logger)
        self._hdlr = None
        self._nbline = 10000

    @property
    def hdlr(self):
        """Return or build a handler on a asrun calculation."""
        if not self._hdlr:
            self._hdlr = self._build_new_hanfler()
        return self._hdlr

    def new_handler(self):
        """Create a new handler for a new calculation.

        This will create a fresh AsterProfil object for the next calculation.
        """
        self._hdlr = None

    def _build_new_hanfler(self):
        """Create a handler to manage the execution."""
        #from asrun import create_calcul_handler

        job_infos = self._case.job_infos
        server = job_infos.server
        if server not in self._infos.available_servers:
            raise RunnerError(translate('Runner', 'Unknown server: {0!r}')
                              .format(server))
        prof = self._infos.init_profil(server)
        if job_infos.jobid:
            prof['jobid'] = job_infos.jobid
            prof['nomjob'] = job_infos.name
            prof['mode'] = text_to_asrun(JobInfos.mode_to_text(job_infos.mode))
        debug_message2("Create handler with:\n", prof)
        return create_calcul_handler(prof)

    def do_refresh(self):
        """Refresh state of currently processed (calculated) result."""
        if self.is_finished() or not self.is_started():
            return
        res = self.hdlr.tail(nbline=self._nbline)
        self.current.state = convert_asrun_state(res.state, res.diag)
        debug_message2('Job status is', res, ':', self.current.state)
        if self.current.state & SO.Finished:
            self._case.job_infos.end_time = current_time()
            self.hdlr.get_results()
            # parse message file if it exists
            stage = self.current_stage
            output = stage.output_file(prefer_message=True)
            if output:
                with open(output, 'rb') as fileout:
                    text = to_unicode(fileout.read())
                    self.current.clear_messages()
                    self.current.add_messages(extract_messages(text))
                    self.current.state |= SO.Nook if 'NOOK' in text else 0
            self._update_result()
            # refresh next if any
            self.refresh()
        else:
            self.console("\nLast {0} lines at {1}..."
                         .format(self._nbline, current_time()), reset=True)
            self.console(res.output)
            # on partial output
            self.current.add_messages(extract_messages(res.output))

    def start_current(self):
        """Activate calculation simulation for next result."""
        stage = self.current_stage
        stages = self.stages_stack + [stage]
        stagename = self._name(stage)
        name = valid_file_name(stagename)
        self.log(translate('Runner', 'Starting "{0}"...').format(stagename))
        job_infos = self._case.job_infos
        try:
            self.new_handler()
            stage.set_remote(job_infos.get('remote_folder'))
            create_profil_for_current(self.hdlr.prof, self._case,
                                      stages, name, self._infos)
            jret, out = self.hdlr.start()
            if jret != 0:
                msg = translate('Runner',
                                'Error during submission of "{0}"'
                                .format(stagename))
                self.log(msg)
                self.log(out)
                raise RunnerError(msg, out)

        except RunnerError as exc:
            self.log("ERROR: {0}".format(exc.msg))
            self.stop()
            raise

        else:
            self.current.state = SO.Pending
            job_infos.jobid = self.hdlr.jobid
            job_infos.name = name
            job_infos.start_time = current_time()
            self.log(translate('Runner',
                               'Stage "{0}" start calculation (jobid={1}, '
                               'queue={2})')
                     .format(stagename, self.hdlr.jobid, self.hdlr.queue))

    def stop_current(self):
        """Stop the current calculation process."""
        if not self.current or self.current.state & SO.Finished:
            return False
        # self.hdlr.kill()
        return True

    def cleanup(self):
        """Cleanup function, called when a RunCase is removed."""
        # Warning: it should be "when a RunCase is deleted"
        # Currently "removed" means "not follow by the dashboard", no?
        # That's why it is currently limited to unittests.
        debug_message2("cleanup execution")
        if self._unittest:
            if not self._case.job_infos.jobid:
                return
            hdlr = self._build_new_hanfler()
            hdlr.kill()

    def _update_result(self):
        """
        Assign calculation state to the first result and remove
        it from list. In successfull case begin simulation for next
        result or interrupt simulation otherwise.
        """
        stagename = self._name(self.current_stage)
        if self.current.state & SO.Success:
            self.log(translate('Runner',
                               'Stage "{0}" calculation succeeded')
                     .format(stagename))
            self._queue.pop(0)
            self.start_next()
        else:
            self.log(translate('Runner',
                               'Stage "{0}" calculation failed. Interruption')
                     .format(stagename))
            self.cancel_next()


class AsRunInfos(ServerInfos, metaclass=Singleton):
    """Proxy object to request asrun informations."""
    _singleton_id = 'asrun_runner.AsRunInfos'
    _cache_run = _stream = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._run = AsRunInfos.asrun_instance(**kwargs)

        ###from asrun import create_client
        
        # self._client = create_client(self._run.rcdir)
        # self._client.init_server_config()
        self._client = None

    @classmethod
    @need_asrun
    def asrun_instance(cls, **kwargs):
        """Return a singleton instance of the main AsterRun object."""
        if not cls._cache_run:
            #from asrun import create_run_instance
            cls._stream = Stream2Func()
            opts = {'log_progress': cls._stream}
            opts['debug_stderr'] = debug_mode() > 1
            if debug_mode() <= 1:
                opts['stderr'] = LogFiles.filename(name='asrun')
            opts.update(kwargs)
            cls._cache_run = None 
            #cls._cache_run = create_run_instance(**opts)
        return cls._cache_run

    @classmethod
    def set_log_callback(cls, callback):
        """Set the function in charge of logging."""
        cls._stream.set_function(callback)

    @property
    def available_servers(self):
        """Return the list of available servers."""
        #return self._client.get_server_list()
        return ["localhost"]

    def server_username(self, server):
        """Return the username to be used on a server.

        Returns:
            str: Username.
        """
        return  getpass.getuser()

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
        return {"stable":"17.2.0"}

    def server_modes(self, server):
        """Give the modes supported by `server`.

        Returns:
            list(str): List of modes (as text).
        """
        modes = []
        cfg = self.server_config(server)
        for name, text in [('batch', JobInfos.BatchText),
                           ('interactif', JobInfos.InteractiveText)]:
            if cfg.get(name, '') in ('oui', 'yes'):
                modes.append(text)
        return modes

    def exec_modes(self):
        """Give the modes supported for debugging.

        Returns:
            list(str): List of modes (as text).
        """
        return (JobInfos.ExecOptimText, JobInfos.ExecDebugText,
                JobInfos.ExecDebuggerText, JobInfos.PrepEnvText)

    def server_config(self, server):
        """Returns a dict with server configuration."""
        #return self._client.get_server_config(server)
        return {}

    def init_profil(self, server):
        """Build a *template* profil for the server"""
        return self._client.init_profil(server)

    def refresh_one(self, server):
        """Refresh the informations of a server.

        Arguments:
            server (str): Server name.

        Returns:
            bool: *True* if it succeeded, *False* otherwise.
        """
        # switch all servers on
        servcfg = self.server_config(server)
        if ping(self.server_hostname(server)):
            servcfg["etat"] = "on"
        ##self._client.refresh_server_config([server])
        return True


class Stream2Func:
    """Proxy for the asrun logger object."""

    def __init__(self):
        self._func = None

    def set_function(self, function):
        """Use the function as stream."""
        self._func = function

    def write(self, string):
        """Write/send a string"""
        # covered by test_engine_asrun.py but needs --nologcapture option
        if self._func: # pragma: no cover
            self._func(string.strip())

    def flush(self):
        """Does nothing."""
