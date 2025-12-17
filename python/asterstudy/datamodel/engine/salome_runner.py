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
Salome runner
-------------

This module defines a runner using SALOME for code_aster executions.

See documentation of *SalomeLauncher*
http://docs.salome-platform.org/latest/tui/KERNEL/interfaceEngines_1_1SalomeLauncher.html
"""


import getpass
import os
import os.path as osp
import shutil
import socket
from glob import glob

from ...common import (CFG, Features, RunnerError, Singleton, current_time,
                       debug_message2, hms2s, info_message, is_localhost,
                       localhost_server, make_dirs, remove_path, secs2hms,
                       str2tuple, timestamp, to_unicode, translate,
                       valid_file_name)
from ..general import FileAttr
from ..job_informations import JobInfos
from ..result import Message, MsgLevel, MsgType
from ..result import StateOptions as SO
from ..result import extract_messages
from .abstract_runner import Runner, ServerInfos
from .edf_servers import adapt_parameters
from .engine_utils import (code_aster_exit_code, convert_launcher_state,
                           convert_state_from_message,
                           create_profil_for_current, kill_aster,
                           parse_server_config, remote_exec, remote_file_copy,
                           remote_tail)

try:
    import salome
    salome.salome_init()
    HAS_SALOME = True
except (ImportError, AttributeError, RuntimeError): # pragma: no cover
    HAS_SALOME = False


def has_salome():
    """Tell if SalomeLauncher is available"""
    return HAS_SALOME


class Salome(Runner):
    """Runner that use SALOME backend.

    Arguments:
        case, logger: see
            :obj:`datamodel.engine.abstract_runner.Runner`.
        unittest (bool): Enable unittest mode.

    Attributes:
        _run (object): AsterRun instance.
        _infos (object): AsRunInfos instance.
        _hdlr (object): SalomeLauncher instance.
    """
    watched_file = osp.join("logs", "output.log.*")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._infos = SalomeInfos()
        # ensure that the resource definition are read
        _ = self._infos.available_servers
        self._hdlr = None
        self._nbline = 10000
        self.xmlfile = osp.join(self._case.model.folder, 'joblist.xml')

    def check_parameters(self):
        """Check parameters before starting."""
        super().check_parameters()
        # check time limit (at least >= 1 minute) and convert to the format
        jinf = self._case.job_infos
        jinf.set('time', secs2hms(max(hms2s(jinf.get('time')), 60)))

    @property
    def hdlr(self):
        """Return or build a handler on a SALOME launcher."""
        if not self._hdlr:
            self._hdlr = \
                salome.naming_service.Resolve('/SalomeLauncher')
        return self._hdlr

    def _init_job(self):
        """Ensure that the job is known by *SalomeLauncher*.

        Returns:
            JobInfos: The job itself.
        """
        job_infos = self._case.job_infos
        if not job_infos.assigned and job_infos.dump_string:
            job_infos.jobid = str(self.hdlr.restoreJob(job_infos.dump_string))
        return job_infos

    def do_refresh(self):
        """Refresh state of currently processed (calculated) result."""
        if self.is_finished() or not self.is_started():
            return
        job_infos = self._init_job()
        # only supported for Adao execution
        if job_infos.get("make_env") and job_infos.use_adao():
            self.current.state = SO.Success
        else:
            res = "FAILED"
            if job_infos.jobid_int >= 0:
                res = self.hdlr.getJobState(job_infos.jobid_int)
                job_infos.dump_string = self.hdlr.dumpJob(job_infos.jobid_int)
            self.current.state = convert_launcher_state(res)
            info_message('Job {0}: status is {1}: {2}'.format(
                job_infos.jobid, res, SO.name(self.current.state)))

        if self.current.state & SO.Finished:
            job_infos.end_time = current_time()
            self.get_job_results()
            # parse message file if it exists
            output = self.current_stage.output_file()
            if output:
                self._update_state_from_output(output, res,
                                               job_infos.mode & JobInfos.Console)
            self._update_result()
            # refresh next if any
            self.refresh()
        else:
            self.console("\nLast {0} lines at {1}..."
                         .format(self._nbline, current_time()), reset=False)
            salome_job = self.hdlr.getJobParameters(job_infos.jobid_int)
            text = remote_tail(self._infos.server_username(job_infos.server),
                               self._infos.server_hostname(job_infos.server),
                               osp.join(salome_job.work_directory,
                                        self.watched_file),
                               self._nbline)
            self.current.add_messages(extract_messages(text))
            self.console(text)

    def start_current(self):
        """Activate calculation simulation for next result."""
        stage = self.current_stage
        stages = self.stages_stack + [stage]
        stagename = self._name(stage)
        name = valid_file_name(stagename)
        self.log(translate('Runner', 'Starting "{0}"...').format(stagename))
        job_infos = self._case.job_infos
        try:
            server = job_infos.get('server')
            servcfg = self._infos.server_config(server)
            verscfg = self._infos.server_versions(server)
            stage.set_remote(job_infos.get('remote_folder'))
            if not servcfg:
                raise RunnerError(translate("Runner",
                                            "Server {0!r} is not available.")
                                  .format(server))
            prof = create_profil_for_current(None, self._case,
                                             stages, name, self._infos)

            # Here, we use asrun utilities to inspect profile
            # These utilities are in | `asrun.plugins.profil`
            #                        | `asrun.common.sysutils`

            # ---- `AsterProfil.get_data` returns a collection
            #          of data (in) entries.

            # ---- Each entry has type *ExportEntry*, inherited from *FileName*,
            #          which has a `host` attribute.
            dbtype, _ = prof.get_base('D')

            # TODO: use asrun's is_remote instead of i.host
            remote_in_files = [i.path for i in prof.get_data()
                               if i.host and i.type != dbtype]
            remote_in_db = [i.path for i in prof.get_data()
                            if i.host and i.type == dbtype]
            salome_job = create_command_job(servcfg, prof, stage, verscfg)
            jobid = self.hdlr.createJob(salome_job)
            try:
                self._infos.export_remote_input_files(server,
                                                      remote_in_files,
                                                      salome_job.work_directory,
                                                      False)
                self._infos.export_remote_input_files(server,
                                                      remote_in_db,
                                                      salome_job.work_directory,
                                                      True)
                info_message("Submitting job on {0}...".format(server))
                self.hdlr.launchJob(jobid)
                info_message("job submitted")
            except Exception as exc:
                msg = translate('Runner',
                                'Error during submission of "{0}"'
                                .format(stagename))
                self.log(msg)
                self.log(to_unicode(exc))
                raise RunnerError(msg, str(to_unicode(exc))) from exc

        except RunnerError as exc:
            self.log("ERROR: {0}".format(exc.msg))
            self.stop()
            raise

        else:
            self.current.state = SO.Pending
            # Store job informations
            job_infos.studyid = prof['studyid'][0]
            job_infos.jobid = str(jobid)
            job_infos.name = name
            job_infos.start_time = current_time()
            job_infos.dump_string = self.hdlr.dumpJob(jobid)
            self.log(translate('Runner',
                               'Stage "{0}" start calculation (jobid={1})')
                     .format(stagename, jobid))

    def stop_current(self):
        """Stop the current calculation process."""
        if not self.current or self.current.state & SO.Finished:
            return False
        self.current.state = SO.Error
        job_infos = self._init_job()
        if not job_infos.assigned:
            return True
        user = self._infos.server_username(job_infos.server)
        host = self._infos.server_hostname(job_infos.server)
        if is_localhost(job_infos.server):
            user = host = None
        if job_infos.mode & JobInfos.Interactive:
            kill_aster(job_infos.studyid, user, host)
        info_message('Stopping job {0}...'.format(job_infos.jobid))
        self.hdlr.stopJob(job_infos.jobid_int)
        self.get_job_results()
        job_infos.dump_string = self.hdlr.dumpJob(job_infos.jobid_int)
        info_message('Job {0} stopped'.format(job_infos.jobid))
        return True

    def cleanup(self):
        """Cleanup function, called when a RunCase is removed."""
        # Warning: it should be "when a RunCase is deleted"
        # Currently "removed" means "not follow by the dashboard", no?
        debug_message2("cleanup execution")

    def _update_state_from_output(self, output, launcher_state, console=False):
        """"Update the "launcher" state from the output.

        Arguments:
            output (str): Output filename.
            launcher_state (int): *JobLauncher* job state.
            console (bool, optional): *True* if the job was executed through a
                terminal.
        """
        if console:
            self.current.state = code_aster_exit_code(output)
        else:
            state = convert_state_from_message(launcher_state, output)
            if state & SO.Success:
                from_exit = code_aster_exit_code(output)
                state = (state ^ SO.Success) | from_exit
            self.current.state = state
        with open(output, 'rb') as fileout:
            text = to_unicode(fileout.read())
            self.current.clear_messages()
            self.current.add_messages(extract_messages(text))
            self.current.state |= SO.Nook if 'NOOK' in text else 0

    def _update_result(self):
        """
        Assign calculation state to the first result and remove
        it from list. In successfull case begin simulation for next
        result or interrupt simulation otherwise.
        """
        stagename = self._name(self.current_stage)
        current = self.current
        copy_error = self._copy_results()
        if copy_error:
            current.state = SO.Error
            self.log(translate('Runner',
                               "{0} result file(s) has(have) not been "
                               "copied to its(their) destination. "
                               "Following stages will probably fail.")
                     .format(copy_error))

        if current.state & SO.Success:
            self.log(translate('Runner',
                               'Stage "{0}" calculation succeeded '
                               'with state {1} ({2})')
                     .format(stagename, SO.name(current.state), current.state))
            self._queue.pop(0)
            self.start_next()
        else:
            self.log(translate('Runner',
                               'Stage "{0}" calculation failed. Interruption')
                     .format(stagename))
            self.cancel_next()

    def _copy_results(self):
        """Copy/move results files to their final destination.

        Note:
            Results are put in the stage directory by the profile,
                they are copied to the path specified by the user
                in this function.
                This does not include result databases, neither
                files left on remote server.
        """
        error = 0
        stage = self.current_stage
        stagedir = stage.folder
        case = self._case
        if case.out_dir:
            src = osp.join(stagedir, osp.basename(case.out_dir))
            out_dir = case.out_dir
            self.log(translate('Runner', "Copying result directory {0!r}")
                     .format(out_dir))
            try:
                make_dirs(out_dir)
                for path in glob(osp.join(src, '*')):
                    dest = osp.join(out_dir, osp.basename(path))
                    remove_path(dest)
                    shutil.move(path, dest)
            except (IOError, OSError) as exc:
                self._add_msg_copy(exc)
                error += 1

        stages = [stage]
        stgi = stage
        while stgi.parent_stage and stgi.parent_stage.is_intermediate():
            stages.append(stgi.parent_stage)
            stgi = stgi.parent_stage

        # files are hold by intermediate stages but in the current stage dir
        seen = set()
        for stgi in reversed(stages):
            for fileinfo in stgi.handle2info.values():
                if fileinfo.attr & FileAttr.Out and not fileinfo.isremote:
                    src = osp.join(stagedir, osp.basename(fileinfo.filename))
                    if src in seen:
                        # already copied for a following stage
                        continue
                    try:
                        dest = fileinfo.filename
                        self.log(translate('Runner', "Copying result {0!r}")
                                 .format(dest))
                        parent = osp.dirname(dest)
                        make_dirs(parent)
                        dest = dest if not osp.isdir(src) else parent
                        shutil.move(src, dest)
                        seen.add(src)
                    except (IOError, OSError) as exc:
                        self._add_msg_copy(exc)
                        error += 1
        return error

    def _add_msg_copy(self, exc):
        """Add a message for an exception raised by a copy failure."""
        txt = translate('Runner',
                        'ERROR: Copy failed: {0}').format(to_unicode(exc))
        info_message(txt)
        self.current.add_messages(
            Message(MsgLevel.Error, txt, MsgType.Runner, "", 0, 0))

    def get_job_results(self):
        """Wrapper for retrieving job results, to handle remote res database.

        Arguments:
            job_infos (JobInfos): Asterstudy's job object.
        """
        job_infos = self._case.job_infos
        if not job_infos.assigned:
            return

        stg, st_res = self.current_stage, self.current
        has_remote = st_res.has_remote or stg.has_remote_files()

        isok = True
        if has_remote: # pragma: no cover
            # Checked by test_engine_salome_remote.py
            # SALOME Launcher's job object
            salome_job = self.hdlr.getJobParameters(job_infos.jobid_int)

            # the remote database is found in `out_files` thanks to its name
            dbpath = stg.database_path

            user = self._infos.server_username(job_infos.server)
            host = self._infos.server_hostname(job_infos.server)
            wrkdir = salome_job.work_directory
            for outfile in salome_job.out_files:
                iret = 0
                # A few tests on the out file
                is_db = outfile == osp.basename(dbpath)
                unit = stg.basename2unit(outfile)
                is_file = unit in stg.handle2info
                is_remote_file = is_file and stg.handle2info[unit].isremote

                # remote database case
                src = osp.join(wrkdir, outfile)
                if is_db and st_res.has_remote:
                    iret = remote_file_copy(user, host, src,
                                            dbpath, True, ignore_errors=True)[0]

                # remote out file case
                elif is_remote_file and not is_db:
                    # TODO: Change False value when implementing REPE_OUT
                    iret = remote_file_copy(user, host, src,
                                            stg.handle2info[unit].relpath,
                                            False, ignore_errors=True)[0]
                else:
                    self.hdlr.getJobWorkFile(job_infos.jobid_int, outfile, "")
                isok = isok and iret == 0

            # copy 'logs' directory that is not in `out_files`
            self.hdlr.getJobWorkFile(job_infos.jobid_int, 'logs', "")
        else:
            self.hdlr.getJobResults(job_infos.jobid_int, "")
        if isok:
            self.hdlr.clearJobWorkingDir(job_infos.jobid_int)


class SalomeInfos(ServerInfos, metaclass=Singleton):
    """Proxy object to request informations about servers in SALOME."""
    _singleton_id = 'salome_runner.SalomeInfos'
    _cache_run = _stream = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._cfg = {}

    @property
    def available_servers(self):
        """Return the list of available servers."""
        # If it is already filled, return
        if self._servers:
            return self._servers
        # Ask for SALOME the known resources
        param = salome.ResourceParameters()
        param.can_launch_batch_jobs = True
        rc_manager = salome.lcc.getResourcesManager()
        self._servers = rc_manager.GetFittingResources(param)
        # Put localhost at first position to ensure a quick refresh
        # at the first opening of Run dialog
        if localhost_server() in self._servers:
            self._servers.remove(localhost_server())
            self._servers.insert(0, localhost_server())
        for server in self._servers:
            self._set_rcdef(server)
        return self._servers

    def _set_rcdef(self, server):
        """Ask Salome Resources Manager for the `rc_definition` of a server.

        Arguments:
            server (str): Name of the server as declared in JobManager.

        Returns:
            *ResourceDefinition*: Resources definition of the server.
        """
        if server not in self._servers:
            return None
        rc_manager = salome.lcc.getResourcesManager()
        rcdef = rc_manager.GetResourceDefinition(server)

        # working_directory is forced on localhost and known edf servers
        def _wrkdir(base):
            return osp.join(base, "asterstudy_workdir_{}".format(getpass.getuser()))

        if not rcdef.working_directory:
            # do not define a directory for at least one server for coverage
            rcdef.working_directory = _wrkdir(os.getenv("HOME", "/tmp"))

            if is_localhost(server):
                rcdef.working_directory = _wrkdir(os.getenv("ASTER_TMPDIR", "/tmp"))

            elif rcdef.hostname.startswith("gaia"):
                rcdef.working_directory = _wrkdir(osp.join('/scratch',
                                                           getpass.getuser()))
            elif rcdef.hostname.startswith("cronos"):
                rcdef.working_directory = _wrkdir(osp.join('/scratch', 'users',
                                                           getpass.getuser()))

        cfg = self.server_config(server)
        cfg['rc_definition'] = rcdef
        return rcdef

    def server_username(self, server):
        """Return the username to be used on a server.

        Returns:
            str: Username.
        """
        # Returns empty str currently in Salome-Meca
        #    because such is the default definition in the ressource.
        # Is this normal?
        rcdef = self.server_config(server).get('rc_definition')
        return getattr(rcdef, 'username', None) or getpass.getuser()

    def server_hostname(self, server):
        """Return the hostname of a server.

        Returns:
            str: Name/IP of the server, None if it is not found.
        """
        rcdef = self.server_config(server).get('rc_definition')
        return getattr(rcdef, 'hostname', None)

    def server_config(self, server):
        """Returns a dict with server configuration."""
        # ensure the servers informations have been read
        if not self._servers:
            _ = self.available_servers
        # initialize it if it does not yet exist
        self._cfg[server] = self._cfg.get(server, {})
        return self._cfg[server]

    def server_versions(self, server):
        """Give the list of available versions on `server`.

        Returns:
            dict: Dict providing the version number (as string) for each
            version ('stable': '14.4.0').
        """
        return self.server_config(server).get('versions_ids', {})

    def server_modes(self, server):
        """Give the modes supported by `server`.

        Returns:
            list(str): List of modes (as text).
        """
        modes = []
        rcdef = self.server_config(server).get('rc_definition')
        batch_system = getattr(rcdef, 'batch', 'none')
        modes = ([JobInfos.InteractiveText, JobInfos.ConsoleText]
                 if batch_system == 'none' else [JobInfos.BatchText])
        return modes

    def exec_modes(self):
        """Give the modes supported for debugging.

        Returns:
            list(str): List of modes (as text).
        """
        return (JobInfos.ExecOptimText, JobInfos.ExecDebugText,
                JobInfos.ExecDebuggerText, JobInfos.PrepEnvText)

    def refresh_one(self, server):
        """Refresh the informations of a server.

        *To check error recovery in unittests, *server* can take a special
        value *"unittest"*, that simulates an *OSError* exception.*

        Arguments:
            server (str): Server name.

        Returns:
            bool: *True* if it succeeded, *False* otherwise.
        """
        _unittest = server == 'unittest'
        server = localhost_server() if _unittest else server
        local = is_localhost(server)
        rcdef = self._set_rcdef(server)
        if not rcdef:
            raise ValueError(translate("Runner",
                                       "Server {0!r} is not available.")
                             .format(server))

        hostname = rcdef.hostname if not local else localhost_server()
        # TODO: replace 'as_run --info' by 'codeaster_services'
        try:
            if _unittest:
                raise OSError
            msg = translate("Runner", "Refreshing configuration on {0}..."
                            .format(hostname))
            cmd = "as_run --info"
            cmd = cmd if local else salome_shell(rcdef.applipath, cmd)
            output = remote_exec(rcdef.username, hostname, cmd,
                                 timeout=15, message=msg)
        except OSError:
            return False

        cfg = self.server_config(server)
        cfg.update(parse_server_config(output))
        debug_message2("Server configuration for {0!r}: {1}"
                       .format(server, cfg))
        return True

    def export_remote_input_files(self, server, flist, workdir, isdir):
        """Method to manually copy already remote input files to work dir.

        Files are copied to workdir with their base names.

        Arguments:
            server (str): name of the SALOME resource.
            flist (list): list of remote files to copy.
            workdir (str): path to execution directory.
            isdir (bool): *True* for directory entries.

        Note:
            For `flist` and `workdir`, paths are related to the resource,
                they are not preceded by [<user>@<host>:].
            This is a dirty workaround, waiting for SALOME Launcher to
                provide a proper implementation of this feature.
        """
        # see the example at
        # http://python-for-system-administrators.readthedocs.io/en/latest/ssh.html
        user = self.server_username(server)
        host = self.server_hostname(server)
        for myfile in flist:
            dest = osp.join(workdir, osp.basename(myfile))
            ret = remote_file_copy(user, host, myfile, dest, isdir,
                                   ignore_errors=True)
            if ret[0] != 0:
                msg = translate("Runner",
                                "Copy of {0}@{1}:{2} to {3} exited with "
                                "code {4[0]}.\n"
                                "Error:\n{4[2]}"
                                .format(user, host, myfile, dest, ret))
                raise IOError(msg)


def create_command_job(servcfg, prof, stage, verscfg):
    """Create the SalomeLauncher job.

    Arguments:
        servcfg (dict): server configuration.
        prof (*AsterProfil*): object defining the study.
        stage (*Stage*): Stage to be executed.
        verscfg (dict): dict of server's versions.
    """
    jinf = stage.parent_case.job_infos
    stagedir = stage.folder
    vers = verscfg.get(jinf.get('version'))
    support = Features(vers and str2tuple(vers))
    export = osp.join(stagedir, "export")
    fname = osp.join(stagedir, "launcher_script")
    prefix = ""
    tmpdir_def = ""
    if is_localhost(jinf.server):
        tmpdir_def = "export ASTER_TMPDIR=" + os.environ["ASTER_TMPDIR"]
    if jinf.get('mode') == JobInfos.Console:
        prof.args['interact'] = ''
        prefix = "${wrap} "
    # TODO: replace 'as_run --getversion_path' by 'codeaster_services'
    with open(fname, "w") as fobj:
        if support["use_run_aster"]:
            runner = "{prefix}${{versroot}}/bin/run_aster export"
        else:
            runner = "{prefix}as_run --num_job={id} export"
        fobj.write(os.linesep.join([
            "#!/bin/bash",
            tmpdir_def,
            "wrap=$(which xterm && echo ' -e ')",
            "versroot=$(as_run --vers={vers} --getversion_path)/../..",
            runner + " 2> ./logs/stderr_command_salome.log",
            ""]).format(id=prof['studyid'][0], prefix=prefix, vers=jinf.get("version")))
    os.chmod(fname, 0o755)

    salome_job = salome.JobParameters()
    salome_job.job_name = str(prof["nomjob"][0])
    salome_job.job_type = "command_salome"
    salome_job.wckey = jinf.get('wckey') or CFG.get_wckey() or ''
    salome_job.job_file = fname
    salome_job.result_directory = stagedir
    salome_job.work_directory = new_directory(servcfg)
    salome_job.maximum_duration = jinf.get('time')
    salome_job.extra_params = jinf.get('extra')

    adapt_parameters(salome_job, jinf)

    # TODO: use asrun's is_remote instead of i.host

    # Provided in files will be copied by Launcher onto execution dir
    #     (remote if necessary)
    local_in_files = [i.path for i in prof.get_data() if not i.host]
    local_in_files.append(export)
    salome_job.in_files = local_in_files

    # Only basenames are provided to the launcher for out files
    out_files = [osp.basename(i.path) for i in prof.get_result()]
    salome_job.out_files = [i.split(":")[-1] for i in out_files]
    salome_job.resource_required = resource_parameters(jinf)

    # Now, profil methods from asrun are called (see profil.py)

    # Deepcopy of the profil object
    exported = prof.copy()

    # Loop study files
    for entry in exported.get_collection():
        # Leave only basename for launcher
        entry.host, entry.user, entry.passwd = '', '', ''
        entry.path = osp.basename(entry.path)

        # Warning: despite of the method's name, the entry
        #    (i.e. asrun obj referencing a file)
        #    is updated in place and not added,
        #    because the entry object is already referenced
        #    by the profil (see implementation in asrun/profil.py).
        # Updating the entry is required to update the export content
        exported.add(entry)
    exported.WriteExportTo(export)
    return salome_job


def resource_parameters(job_infos):
    """Create ResourceParameters from the job parameters"""
    debug_message2("ResourceParameters from:", job_infos.asdict())
    use_batch = job_infos.get('mode') == JobInfos.Batch
    res = salome.ResourceParameters()
    res.name = str(job_infos.get('server'))
    res.can_launch_batch_jobs = use_batch
    # setting mem_mb raises "ulimit: error setting limit (Invalid argument)" on localhost
    if not is_localhost(res.name):
        res.mem_mb = int(job_infos.get('memory'))
    res.nb_proc = job_infos.get('mpicpu') or 1
    res.nb_node = job_infos.get('nodes') or 1
    return res

def new_directory(servcfg):
    """Return a new directory that should be unique, even on a remote server.

    Arguments:
        servcfg (dict): server configuration as stored by `SalomeInfos`.

    Returns:
        str: Path to a temporary directory on the remote server.
    """
    return unique_directory(
        getattr(servcfg.get('rc_definition', None), "working_directory", False)
        or servcfg['proxy_dir'],
        socket.gethostname())

def unique_directory(prefix, hostname):
    """Return a unique directory name.

    Arguments:
        prefix (str): The base directory.
        hostname (str): Host name.

    Returns:
        str: Path to a temporary directory on the host.
    """
    return osp.join(prefix,
                    "{0}-{1}-{2}".format(getpass.getuser(),
                                         hostname,
                                         timestamp(as_path=True)))

def salome_shell(applipath, cmd):
    """Returns command line within 'salome shell'.

    Arguments:
        applipath (str): Path of the SALOME application.
        cmd (str): Command line to execute.

    Returns:
        str: Command line wrapped by 'salome shell'.
    """
    return "{0} shell -- {1}".format(osp.join(applipath), cmd)
