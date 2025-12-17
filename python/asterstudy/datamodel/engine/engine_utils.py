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
asrun utilities
---------------

This module allows to manipulate asrun objects.

"""

import os
import os.path as osp
import platform
import re
import signal
import subprocess as SP
from collections import OrderedDict, defaultdict
from functools import wraps
from math import log10

from ...common import (AsterStudyError, Features, RunnerError, copy_file,
                       debug_message, debug_message2, hms2s, localhost_server,
                       make_dirs, no_new_attributes, str2tuple, to_unicode,
                       translate, version)
from ...common.conversion import FileProvider
from ...common.execution import MPIPrefix
from ...common.extfiles import external_file_export_to_med, gen_mesh_file_name
from ...common.remote_utils import make_remote_path, remote_exec, url_gio2asrun
from ..aster_parser import add_debut_fin, is_cmd_called
from ..general import FileAttr
from ..job_informations import JobInfos
from ..result import StateOptions
from ..stage import UsageOptions as UO
from .basics import version_ismpi


def has_asrun():
    """Tell if asrun is available"""
    if getattr(has_asrun, 'cache', None) is not None:
        return has_asrun.cache
    try:
        # pragma pylint: disable=unused-import
        from asrun import create_run_instance
        has_asrun.cache = True
    except ImportError:
        has_asrun.cache = False
    return has_asrun.cache


def need_asrun(func):
    """Decorator that ensures that asrun is available."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        """wrapper"""
        ### TODO : Basile 
        #if not has_asrun(): # pragma: no cover
            #raise ImportError("Import of asrun package failed!")
        return func(*args, **kwargs)
    return wrapper


def _convert_asrun_state(job_state):
    """Convert state value from asrun (job state only) to asterstudy.

    Returns:
        state (StateOptions): state of the job or 0 if job is ended.
    """
    state = 0
    if job_state in ('_', 'PEND', 'SUSPENDED'):
        state = StateOptions.Pending
    elif job_state == 'RUN':
        state = StateOptions.Running
    debug_message2("AsRun state {0} => {1}"
                   .format(job_state, StateOptions.name(state)))
    return state

def _convert_launcher_state(job_state, full=False):
    """Convert state value from SalomeLauncher to asterstudy.

    Returns:
        state (StateOptions): state of the job or 0 if job is ended.
    """
    state = 0
    if job_state == 'RUNNING':
        state = StateOptions.Running
    elif job_state == 'PAUSED':
        # Pausing not used with code_aster
        state = StateOptions.Pending
    elif job_state not in ("FINISHED", "FAILED"):
        state = StateOptions.Pending
    elif full:
        if job_state == "FINISHED":
            state = StateOptions.Success
        else:
            state = StateOptions.Error
    debug_message2("Launcher state {0} => {1}"
                   .format(job_state, StateOptions.name(state)))
    return state

def code_aster_exit_code(filename):
    """Return the exit code of the execution.

    Returns:
        *StateOptions*: State from exit code.
    """
    iret = 4
    regexp = re.compile("EXECUTION_CODE_ASTER_EXIT.*= *(?P<iret>[0-9]+)", re.M)
    if osp.isfile(filename):
        with open(filename, encoding='utf-8', errors='ignore') as fmess:
            irets = [int(mat.group("iret"))
                     for mat in regexp.finditer(fmess.read())]
            iret = max(irets) if irets else 1
    return StateOptions.from_exit(iret)

def _convert_asrun_diag(diag):
    """Convert diagnostic from asrun to asterstudy."""
    if diag == 'OK' or diag.startswith('<A>'):
        state = StateOptions.Success
        if diag.startswith('<A>'):
            state = state | StateOptions.Warn
    elif '<S>' in diag:
        state = StateOptions.Interrupted
    else:
        state = StateOptions.Error

    # additionnal flags
    if 'NOOK' in diag or 'TEST_RESU' in diag:
        state = state | StateOptions.Nook

    if 'CPU_LIMIT' in diag:
        state = state | StateOptions.CpuLimit
    elif 'MEMORY' in diag:
        state = state | StateOptions.Memory
    elif 'NO_CONVERGENCE' in diag:
        state = state | StateOptions.NoConvergence

    debug_message2("AsRun diag {0} => {1}"
                   .format(diag, StateOptions.name(state)))
    return state

def convert_asrun_state(job_state, job_diag):
    """Convert state/diag values from asrun to asterstudy."""
    state = _convert_asrun_state(job_state)
    if state:
        return state
    state = _convert_asrun_diag(job_diag)
    return state

def convert_launcher_state(job_state, job_diag=None):
    """Convert state/diag values from SalomeLauncher to asterstudy.

    If `job_diag` is ``None``, only `job_state` is used.
    Otherwise, `job_diag` is only used if the job is finished.

    Arguments:
        job_state (str): Job state as returned by SalomeLauncher.
        job_diag (str): Diagnostic as returned by asrun (or None).
    """
    state = _convert_launcher_state(job_state, full=job_diag is None)
    if state:
        return state
    state = _convert_asrun_diag(job_diag)
    return state

def convert_state_from_message(job_state, filename):
    """Shortcut to call `convert_launcher_state` with the message file."""
    return convert_launcher_state(job_state, asrun_diag(filename))

def asrun_diag(filename):
    """Return the asrun diagnostic from an output file."""
    if osp.basename(filename) == 'message':
        # code_aster_exit_code will be called later
        return 'OK'
    diag = '<F>_SYSTEM'
    if osp.isfile(filename):
        re_status = re.compile(r'\-\-\- DIAGNOSTIC JOB : +(.*?) *$')
        re_cpu = re.compile('cpu *time *limit', re.I)
        with open(filename, "rb") as fobj:
            for line in fobj:
                line = line.decode("utf-8", "ignore")
                if re_cpu.search(line):
                    diag = '<F>_CPU_LIMIT'
                mat = re_status.search(line)
                if mat:
                    diag = mat.group(1)
    return diag


def text_to_asrun(mode):
    """Convert a job mode from the gui label to a string for asrun."""
    mode = mode or JobInfos.BatchText
    if isinstance(mode, int):
        mode = JobInfos.mode_to_text(mode)
    return {
        JobInfos.BatchText: 'batch',
        JobInfos.InteractiveText: 'interactif',
        JobInfos.ConsoleText: 'interactif'
    }[mode]


def exec_to_asrun(mode):
    """Convert a debug mode from the gui label to a string for asrun."""
    mode = mode or JobInfos.ExecOptimText
    return {
        JobInfos.ExecOptimText: ('make_etude', 'nodebug'),
        JobInfos.ExecDebugText: ('make_etude', 'debug'),
        JobInfos.ExecDebuggerText: ('make_dbg', 'debug'),
        JobInfos.PrepEnvText: ('make_env', 'debug'),
    }[mode]


def counter():
    """Returns a counter of execution to pass a unique id for each run."""
    if not hasattr(counter, "idx"):
        counter.idx = 0
    counter.idx += 1
    return counter.idx


def create_profil_for_current(prof, case, stages, jobname, infos):
    """Create the AsterProfil object for one or more stages.

    If more than one stage is given, the first ones are supposed to be
    *intermediate* stages and the last one is *reusable*.

    Arguments:
        prof (AsterProfil): Object with the server informations.
        case (Case): Case object which the stage belongs to.
        stages (list[Stage]): Stage objects to be run.
        jobname (str): Job name.
        infos (*ServerInfos*): Servers configurations.

    Returns:
        AsterProfil: The profile itself, changed in place.
    """
    # pragma pylint: disable=too-many-locals
    from asrun import create_profil
    prof = prof or create_profil()
    jinf = case.job_infos

    prof['actions'], prof['debug'] = exec_to_asrun(jinf.get('execmode'))
    prof['nomjob'] = jobname
    prof['origine'] = "AsterStudy {}".format(version())
    prof['mode'] = text_to_asrun(jinf.get('mode'))
    update_prof(prof, jinf)

    studyid = "{0}-{1:04d}-{2}".format(os.getpid(), counter(), platform.node())
    prof['studyid'] = studyid

    # first and last stages
    first = stages[0]
    last = stages[-1]

    # export files
    destdir = last.folder
    try:
        os.makedirs(destdir)
    except OSError as exc:
        raise RunnerError("Previous results already exist in {0}"
                          .format(destdir)) from exc

    vers = infos.server_versions(jinf.get('server')).get(jinf.get('version'))
    support = Features(vers and str2tuple(vers))
    for path in export_comm(stages, jobname, support, destdir,
                            lang=jinf.get('language'),
                            console=jinf.get('mode') == JobInfos.Console):
        prof.add_entry(path, data=True, type='comm', ul=1)

    # add files of previously executed stages as data
    ancestor = None
    for stgi in case[:first]:
        debug_message2("previous stage:", stgi)
        for unit, fileinfo in stgi.handle2info.items():
            kwargs = asrun_info(unit, fileinfo, stgi.folder)
            kwargs['data'] = True
            kwargs['result'] = False
            prof.add_entry(**kwargs)
        ancestor = stgi

    # add input and output directories if present
    if case.in_dir:
        prof.add_entry(case.in_dir, data=True, type='repe', isrep=True, ul=0)
    if case.out_dir:
        prof.add_entry(case.out_dir, result=True, type='repe', isrep=True, ul=0)

    # data/result files
    seen = set()
    for stgi in stages:
        for unit, fileinfo in stgi.handle2info.items():
            key = (unit, fileinfo.filename)
            if not fileinfo.attr & FileAttr.Out and key in seen:
                continue
            args = asrun_info(unit, fileinfo, stgi.folder)
            prof.add_entry(**args)
            seen.add(key)

    # add message file as result
    prof.add_entry(pathname=osp.join(destdir, 'message'),
                   result=True,
                   ul=6,
                   type='mess')
    # database
    if not jinf.get('no_database') and not last.is_without_db():
        prof.add_entry(pathname=database_path(last, infos, jinf.get('server')),
                       result=True,
                       type='base',
                       compr=jinf.get('compress'),
                       isrep=True)
    if ancestor is not None or first.database:
        if first.database:
            dbpath = first.database
            compr = osp.exists(osp.join(dbpath, "glob.1.gz"))
        else:
            dbpath = database_path(ancestor, infos, jinf.get('server'))
            compr = ancestor.parent_case.job_infos.get('compress')
        prof.add_entry(pathname=dbpath,
                       data=True,
                       type='base',
                       compr=compr,
                       isrep=True)
    debug_message2("Profil generated:\n", prof.get_content())
    return prof

def database_path(stage, infos, server):
    """
    Result database path based on stage and server config.

    Arguments:
        stage (Stage): stage the database belongs to.
        infos (*ServerInfos*): servers configurations.
        server (str): server name.

    Returns:
        str: path of the database.

    Note:
        If the path is remote, it is preceded by `hostname:`.
    """
    # database
    if stage.result.has_remote:
        user = infos.server_username(server)
        host = infos.server_hostname(server)
        return make_remote_path(user, host, stage.database_path)
    return stage.database_path

def _enclosed(text):
    # in case of error, considers to be run separately
    try:
        res = (is_cmd_called(text, "DEBUT") or
               is_cmd_called(text, "POURSUITE") or
               is_cmd_called(text, "FIN"))
    except AsterStudyError:
        res = True
    return res

def export_comm(stages, jobname, support=None, destdir=None, separated=False,
                parametric=False, testcase=False, lang=None, console=False):
    """Return a list of comm files to run stages.

    If neither DEBUT/FIN exists, the content of comm files can be concatenated
    else several files are generated.

    Arguments:
        stages (list[Stage]): Stages to run.
        jobname (str): Name of the job.
        support (Optional[Features]): Supported features of target version.
        destdir (str): Destination directory (default: last stage folder).
        separated (Optional[bool]): If *True* it always separates each stage in
            a different comm file.
        parametric (bool): If *True*, export file for a parametric study.
        testcase (bool): If *True*, export file for a code_aster testcase.
        lang (str): Language to be used or *None*.
        console (bool): If *True*, the commands will be run in a console.

    Returns:
        list[str]: List of filenames of the generated comm files.
    """
    # pragma pylint: disable=too-many-locals
    init0 = stages[0].number + (1 if stages[0].usage & UO.LoadDatabase else 0)
    def _add_buffer(ltext, buff):
        if not buff:
            return
        start = len(ltext) + init0 == 1
        ltext.append(add_debut_fin(buff, start, lang, console))

    add_ids = not (testcase or parametric)
    buff = str("")
    texts = []
    idx = 0
    for stage in stages:
        txt = stage.get_text(support=support,
                             add_ids=add_ids,
                             format_id="{{id}}:{0}".format(stage.number),
                             parametric=parametric)
        if _enclosed(txt) or separated:
            _add_buffer(texts, buff)
            _add_buffer(texts, txt)
            buff = str("")
            idx = 0
        else:
            buff += str(os.linesep) + txt
            idx += stage.nb_commands
    _add_buffer(texts, buff)

    nb_digits = int(log10(max(1, len(texts)))) + 1
    ext = '.com{{0:0{0}}}'.format(nb_digits)

    destdir = destdir or stages[-1].folder
    make_dirs(destdir)
    root = re.sub(r'\.comm$', '', jobname)
    files = []
    for i, txt in enumerate(texts):
        path = osp.join(destdir, root + (ext.format(i) if i > 0 else '.comm'))
        with open(path, "w") as comm:
            comm.write(txt)
        files.append(path)

    return files


def asrun_info(unit, info, folder):
    """Build informations for an asrun file from a
    :obj:`datamodel.file_descriptors.Info` object.

    ``INPUTS`` file for parametric studies has a specific export type.

    Arguments:
        unit (int): Number of logical unit.
        info (datamodel.file_descriptors.Info): Object to export.
        folder (str): Export folder.

    Returns:
        dict: Keyword arguments for asrun Entry.
    """
    if info.must_exist and not info.exists:
        msg = (translate('Runner', "No such file: {0!r}. "
                         "Please check the Case View/DataFiles tab.")
               .format(info.filename))
        if info.isreference:
            msg = translate('Runner', "The mesh object does not exist anymore. "
                            "Please check objects in the Mesh module.")
        raise RunnerError(msg)
    if not info.filename:
        raise RunnerError(translate('Runner',
                                    "filename not defined for unit {0}")
                          .format(unit))

    # WARNING: for now, remote, reference and embedded are mutually exclusive.
    # Convert gio to asrun syntax for remote files given as urls
    filename = url_gio2asrun(info.filename)
    if info.isreference:
        make_dirs(folder)
        filename = _smesh2med(info.filename, folder)
    elif not info.isremote:
        # Local external or embedded file
        filename = osp.join(folder, info.filename)

    ftype = 'libr'
    if info.attr & FileAttr.Named:
        ftype = 'nom'
        unit = 0
    kwargs = dict(pathname=filename,
                  data=bool(info.first_attr & FileAttr.In),
                  result=bool(info.attr & FileAttr.Out),
                  type=ftype,
                  ul=unit)
    return kwargs

def _smesh2med(ref, folder):
    """
    Export an SMESH object into a MED file located in `folder`.

    The name of that MED file in generated automatically.

    Arguments:
        ref (str): the entry of the object.
        folder (str): dirname where to create file.

    Returns:
        str: the absolute path of the MED file just created.
    """
    bname = gen_mesh_file_name(ref, "med")
    filepath = osp.join(folder, bname)
    if not osp.isfile(filepath):
        external_file_export_to_med(ref, filepath)
    return filepath

@need_asrun
def create_asrun_profil(filename):
    """Create a asrun profile from a filename.

    Arguments:
        filename (str): Name of the file to import ('.export' or '.astk').

    Returns:
        *AsterProfil*: asrun object.
    """
    from asrun import create_profil
    filetype = get_filetype(filename)
    if filetype == 'export':
        prof = create_profil(filename)
    elif filetype == 'astk':
        prof = astk2export(filename)
    else:
        raise TypeError("unknown file type.")
    return prof

def add_stages_from_astk(case, filename, force_text=False):
    """Add stages by importing a file from ASTK.

    Arguments:
        case (Case): Case object to create.
        filename (str): Path to the export to create.
        force_text (Optional[bool]): Keep stages in text mode.

    Returns:
        dict: Parameters dict.
    """
    prof = create_asrun_profil(filename)
    prof.absolutize_filename(filename)
    debug_message("Export to import:\n", prof.get_content())
    commfiles, others = prof.get_type('comm', with_completion=True)
    commfiles = sort_comm_files(commfiles)

    provider = FileProvider(case.model.extern_data_path)
    dict_others = {}
    for afile in others:
        if afile.isrep:
            if afile.data:
                case.in_dir = afile.path
            if afile.result:
                case.out_dir = afile.path
        if afile.compr:
            raise TypeError("compressed data files are not yet supported.")
        if afile.ul != 0:
            dict_others[afile.ul] = afile
            provider.add("unit:{0}".format(afile.ul), afile.path)
        else:
            key = osp.basename(afile.path)
            dict_others[key] = afile
            provider.add("data:{0}".format(key), afile.path)

    for comm in commfiles:
        with open(comm.path, 'rb') as fcomm:
            text = fcomm.read()
        rootname = osp.splitext(osp.basename(comm.path))[0]
        case.text2stage(text, rootname,
                        force_text=force_text, provider=provider)

    for stage in case.stages:
        if stage.is_graphical_mode():
            loop_on = stage.handle2info.keys()
        else:
            # add all known files
            loop_on = dict_others.keys()
        for unit in loop_on:
            info = stage.handle2info[unit]
            if info.filename is None and dict_others.get(unit) is not None:
                afile = dict_others[unit]
                info.filename = afile.path
                if afile.data:
                    info.attr |= FileAttr.In
                if afile.result:
                    info.attr |= FileAttr.Out
                if afile.type == "nom":
                    info.attr |= FileAttr.Named
    params = from_asrun_params(prof, with_default=False)
    case.job_infos.add_defaults(overwrite=True)
    case.job_infos.set_parameters_from(params)


def sort_comm_files(collection):
    """Sort comm files: comm first, then com[0-9] in alphabetic order,
    keep initial order when extensions are identical.

    Arguments:
        collection (EntryCollection): asrun object containing list of files.

    Return:
        EntryCollection: sorted list.
    """
    getext = lambda x: osp.splitext(x.path)[1]
    extfiles = sorted([(getext(entry), i, entry) \
                           for i, entry in enumerate(collection)])
    result = [entry for ext, i, entry in extfiles if ext == '.comm']
    result.extend([entry for ext, i, entry in extfiles if ext != '.comm'])
    return result


def get_filetype(filename):
    """Return the type of the file to import.

    Arguments:
        filename (str): Path to the file.

    Returns:
        str: One of 'astk', 'export' or '' if the type is unknown.
    """
    filetype = ''
    expr1 = re.compile('^ *[PAFR] +')
    expr2 = re.compile('^etude,fich,[0-9]+,')
    with open(filename) as fileobj:
        while not filetype:
            try:
                snippet = next(fileobj)
            except StopIteration:
                break
            if expr1.search(snippet):
                filetype = 'export'
                break
            if expr2.search(snippet):
                filetype = 'astk'
                break
    return filetype


@need_asrun
def astk2export(filename):
    """Create a AsterProfil object from a '.astk' file."""
    from asrun import create_profil
    expr = re.compile('^etude,fich,(?P<idx>[0-9]+),'
                      r'(?P<key>\w+) +(?P<value>.*)$ *', re.M)

    with open(filename) as fileobj:
        content = fileobj.read()
    entries = defaultdict(dict)
    for mat in expr.finditer(content):
        line = entries[mat.group('idx')]
        line[mat.group('key')] = mat.group('value')

    prof = create_profil()
    for entry in entries.values():
        prof.add_entry(pathname=entry['nom'],
                       type=entry['type'],
                       ul=int(entry['UL']),
                       data=bool(int(entry['donnee'])),
                       result=bool(int(entry['resultat'])),
                       compr=bool(int(entry['compress'])),
                       isrep=entry['FR'] == 'R')
    return prof


def parse_server_config(content):
    """Parse information write by as_run --info"""
    info = {}
    mat = re.search("@PARAM@(.*)@FINPARAM@", content, re.DOTALL)
    if mat is not None:
        for line in mat.group(1).splitlines():
            try:
                key, val = re.split(' *: *', line)
                info[key] = val
            except ValueError:
                pass
    mat = re.search("@VERSIONS@(.*)@FINVERSIONS@", content, re.DOTALL)
    if mat is not None:
        lvers = []
        for line in mat.group(1).splitlines():
            try:
                key, val = re.split(' *: *', line)
                lvers.append(val)
            except ValueError:
                pass
        lvers = [str(i) for i in lvers]
        info['vers'] = ' '.join(lvers)
    info['versions_ids'] = OrderedDict.fromkeys(lvers)
    mat = re.search("@VERSIONS_IDS@(.*)@FINVERSIONS_IDS@", content, re.DOTALL)
    if mat is not None:
        for line in mat.group(1).splitlines():
            try:
                key, val = re.split(' *: *', line)
                info['versions_ids'][key] = val
            except ValueError:
                pass
    return info


def _diffvers(vers1, vers2, valabs=True):
    """Compute a distance between two versions provided as tuples."""
    func = abs if valabs else lambda x: x
    return [func(i - j) for i, j in zip(vers1, vers2)]

def nearest_versions(ref, versdict):
    """Return the versions sorted from the nearest from `ref`.

    Arguments:
        ref (tuple[int]): Version number to be searched.
        versdict (dict): Dict of available versions with their number.

    Returns:
        tuple: Tuple containing a boolean that tells if exactly the same version
        was found and the versions sorted from the nearest to the farest.
    """
    if not versdict:
        return False, ()

    lvers = []
    i = 0
    for vers, num in versdict.items():
        i += 1
        if num is None:
            num = ""
        lvers.append((_diffvers(ref, str2tuple(num)), i, vers, num))
    lvers = sorted(lvers)
    exact = tuple(lvers[0][0]) == (0, 0, 0)
    return exact, [i[2] for i in lvers]



def remote_file_copy(user, host, source, dest, isdir, ignore_errors=False):
    """SSH file copy from a remote location to another remote location.

    Arguments:
        user (str): User name on the remote host.
        host (str): Host name to be addressed by SSH.
        source (str): Path of the source file, (relative to remote host).
        dest (str): Path of the destination file, remote.
        isdir (bool): *True* if a directory should be copied.
        ignore_errors (bool): Do not raise exceptions in case of error.

    Returns:
        int|tuple: Depends on `ignore_errors`, see `:func:remote_exec`.
    """
    flags = "-r" if isdir else ""
    parentdir = osp.dirname(dest)
    command = ("mkdir -p {parent} ; cp {flags} {source} {dest}"
               .format(parent=parentdir, flags=flags, source=source, dest=dest))
    return remote_exec(user, host, command, ignore_errors)


def remote_tail(user, host, pattern, nbline):
    """Search for a remote file on *host* that matches *pattern* and return
    its last *nbline* lines.

    Arguments:
        user (str): User name on the remote host.
        host (str): Host name to be addressed by SSH.
        pattern (str): Pattern/filename.

    Returns:
        str: Last *nbline* of the file.
    """
    mpi_prefix = MPIPrefix(proc0=False)
    mpi_filter = "".join([" | egrep -v -- '{}'".format(expr)
                          for expr in mpi_prefix.regexp])
    msg = translate("Runner", "Getting job output on {0}...").format(host)
    text = remote_exec(user, host,
                       "cat {1} {2} | tail --lines {0}"
                       .format(nbline, pattern, mpi_filter),
                       ignore_errors=True,
                       message=msg)[1]
    text = text or translate("Runner", "Cannot read output file or empty file.")
    return to_unicode(text)


def kill_aster(jobid, user=None, host=None):
    """Kill a code_aster process executed in interactive mode.

    Arguments:
        jobid (str): String passed to identify the process.
        user (str): Username of the remote server.
        host (str): Hostname of the remote server.

    Returns:
        int: PID of the process killed, -1 if not found, 999999 if executed
        on a remote server.
    """
    mode = 'interactif'
    if not user and not host:
        proc = SP.Popen(['ps', '-e', '--width=512', '-opid', '-ocommand'],
                        stdout=SP.PIPE)
        proc.wait()
        psout = proc.stdout.read().decode()
        proc.stdout.close()
        exp = re.compile(r"^ *([0-9]+) +(.*)\-\-num_job={0}.*\-\-mode={1}"
                         .format(jobid, mode), re.MULTILINE)
        res = exp.findall(psout)
        res.reverse()  # the relevant process should be the last one
        debug_message2("code_aster processes :", res)
        numpr = -1
        cmd = ""
        for numj, cmd in res:
            # "sh -c" is automatically added by os.system
            if cmd.find("sh -c") < 0:
                numpr = int(numj)
                break
        if numpr >= 0:
            debug_message("Terminating process {0}: {1}".format(numpr, cmd))
            os.kill(numpr, signal.SIGKILL)
    else:
        # equivalent using a shell command to be used with ssh
        cmd = ('kill -9 $(ps -e --width=512 -opid -ocommand | '
               'grep -- --num_job={0} | grep -- --mode={1} | '
               'grep -v "sh -c" | tail -1 | sed -e "s/ .*//g" )'
               .format(jobid, mode))
        msg = translate("Runner",
                        "Terminating job {0} on {1}...".format(jobid, host))
        remote_exec(user, host, cmd, ignore_errors=True, message=msg)
        numpr = 999999
    return numpr


def update_prof(prof, job_infos):
    """Update asrun object with parameters from the asterstudy engine.

    *prof* is modified in place.

    Arguments:
        prof (*AsterProfil*): asrun object that defines the execution.
        job_infos (*JobInfos*): *JobInfos* object.
    """
    def _iceil(value):
        if value:
            value = int(value)
        return value
    # ensure to have at least the default parameters
    jinf = JobInfos(with_default=True)
    jinf.set_parameters_from(job_infos.asdict())
    pnames = {'server': ('server', localhost_server(), None),
              'memory': ('memory_limit', 2048, None),
              'time': ('time_limit', '15:00', hms2s),
              'version': ('version', 'stable', None),
              'mpicpu': ('mpi_nbcpu', 1, int),
              'nodes': ('mpi_nbnoeud', 1, int),
              'threads': ('ncpus', 1, _iceil)}
    if not version_ismpi(jinf.get("version")):
        jinf.set("mpicpu", 1)
        jinf.set("nodes", 1)
    for par, arg in pnames.items():
        value = jinf.get(par) if jinf.is_defined(par) else arg[1]
        if arg[2]:
            try:
                value = arg[2](value)
            except Exception: # pragma pylint: disable=broad-except
                # take the default if the conversion failed
                value = arg[1]
        prof[arg[0]] = value

    if jinf.get('args'):
        prof.args['args'] = (prof.args.get('args', '') + " " +
                             jinf.get('args')).strip()


def from_asrun_params(prof, with_default=True):
    """Extract execution parameters from a asrun object.

    Arguments:
        prof (*AsterProfil*): asrun object that defines the execution.
        with_default (bool): If *True* the returned dict will contain default
            values for all parameters. Otherwise only parameters found in `prof`
            will be set.

    Returns:
        dict: Parameters dict.
    """
    pnames = {'server': ('server', None),
              'memory': ('memory_limit', None),
              'time': ('time_limit', None),
              'version': ('version', None),
              'mpicpu': ('mpi_nbcpu', int),
              'nodes': ('mpi_nbnoeud', int),
              'threads': ('ncpus', int),}
    params = JobInfos.Commons.copy() if with_default else {}
    for name, args in pnames.items():
        value = prof[args[0]][0]
        if value == '':
            continue
        if args[1] is not None:
            value = args[1](value)
        params[name] = value
    return params


class ExportCase:
    """Export a Case, see `factory` for different options.

    Arguments:
        case (Case): Case object to export.
        export_name (str): Filename of export file. Additional files will
            be added into its parent directory.
    """
    case = stages = filename = prof = None
    destdir = name = None

    __setattr__ = no_new_attributes(object.__setattr__)

    @staticmethod
    def factory(case, export_name, testcase=False, parametric=False):
        """Create the ExportCase object depending of selected options.

        Arguments:
            case (Case): Case object to export.
            export_name (str): Filename of export file. Additional files will
                be added into its parent directory.
            testcase (bool): If *True*, export case to prepare a testcase.
            parametric (bool): If *True*, export case for a parametric study.
        """
        assert parametric or testcase, "invalid arguments"
        if parametric:
            class_ = ExportParametricCase
        elif testcase:
            class_ = ExportTestCase
        return class_(case, export_name)

    def __init__(self, case, export_name):
        """Initialization."""
        self.case = case
        self.stages = case.stages
        self.filename = export_name
        self.prof = None

        self.destdir, basn = osp.split(export_name)
        self.name = osp.splitext(basn)[0]

    def set_last_stage(self, stage_number):
        """Define the last stage to be exported.

        Arguments:
            stage_number (int): Number of the last stage to export. The
                following stages are ignored.
        """
        self.stages = list(self.case[:stage_number])

    def create_profile(self):
        """Create the asrun profile object."""
        from asrun import create_profil
        self.prof = prof = create_profil()
        # waiting for option in create_profil
        prof._auto_param = False # pragma pylint: disable=protected-access
        prof['actions'] = 'make_etude'

        # add parameters into the asrun profile
        update_prof(prof, self.case.job_infos)

    def export_comm(self, **opts):
        """Export the Commands files."""
        for path in export_comm(self.stages, self.name, None, self.destdir,
                                **opts):
            self.prof.add_entry(path, data=True, type='comm', ul=1)

    def export_data_files(self):
        """Export the data files."""
        seen = set()
        for stgi in self.stages:
            for unit, fileinfo in stgi.handle2info.items():
                args = asrun_info(unit, fileinfo, self.destdir)
                path = args['pathname']
                seen.add(path)
                self.prof.add_entry(**args)
                if fileinfo.attr & FileAttr.In:
                    copy_file(path, osp.join(self.destdir, osp.basename(path)))

    def export_input_dir(self):
        """Export input directory"""
        if self.case.in_dir:
            self.prof.add_entry(self.case.in_dir, data=True, type='repe',
                                isrep=True, ul=0)

    def write_export(self):
        """Write the export file."""
        # keep only basenames
        self.prof.relocate(None, "")
        self.prof.WriteExportTo(osp.join(self.destdir, self.name + ".export"))

    def generate(self):
        """Generate files."""
        self.create_profile()
        self.export_comm()
        self.export_data_files()
        self.export_input_dir()
        self.write_export()

    def get_input_files(self):
        """Returns the list of input files and directories.

        Returns:
            list[str]: List of path names.
        """
        if self.prof:
            return [entry.path for entry in self.prof.get_data()]
        return []


class ExportTestCase(ExportCase):
    """Export a Case to prepare a code_aster test case."""

    def export_comm(self):  # pragma pylint: disable=arguments-differ
        """Export the Commands files."""
        super().export_comm(testcase=True)

    def create_profile(self):
        """Create the asrun profile object."""
        super().create_profile()
        del self.prof['version']
        del self.prof['actions']
        self.prof['testlist'] = 'verification sequential'

    def export_data_files(self):
        """Export the data files."""
        seen = set()
        for stgi in self.stages:
            for unit, fileinfo in stgi.handle2info.items():
                # data files only
                if fileinfo.attr & FileAttr.Out:
                    continue
                args = asrun_info(unit, fileinfo, self.destdir)
                path = args['pathname']
                ext = osp.splitext(path)[1]
                basn = self.name + ext
                i = 0
                while basn in seen:
                    i += 1
                    basn = "{0}_{1}{2}".format(self.name, i, ext)
                seen.add(basn)
                args['pathname'] = basn
                self.prof.add_entry(**args)
                copy_file(path, osp.join(self.destdir, basn))


class ExportParametricCase(ExportCase):
    """Export a Case for a parametric study."""

    def export_comm(self):  # pragma pylint: disable=arguments-differ
        """Export the Commands files."""
        super().export_comm(parametric=True)

    def export_data_files(self):
        """Export the data files."""
        from ..parametric import INPUTS

        super().export_data_files()
        self.prof.add_entry(pathname=INPUTS,
                            data=True,
                            result=False,
                            type='nom',
                            ul=0)
