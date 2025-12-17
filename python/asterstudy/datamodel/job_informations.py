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
Job informations
----------------

This module implements the informations required to execute a job and refresh
its state, even after a save/reload. It also provides the storage for the
parameters entered in the *Run dialog*.
"""

from copy import deepcopy

from ..common import CFG, localhost_server, no_new_attributes, translate


class JobInfos:
    """Implementation of the job informations.

    It stores the execution parameters (server, version, memory limit...) and
    data needed to run a study for Persalys or Adao.
    """
    # pragma pylint: disable=too-many-instance-attributes
    Aster = 0
    Persalys = 1
    Adao = 2
    # !!! keep consistency with asterstudy.proto for serialization !!!
    Null = 0x00
    Batch = 0x01
    Interactive = 0x02
    Console = Interactive | 0x04
    BatchText = translate("Dashboard", "Batch")
    InteractiveText = translate("Dashboard", "Interactive")
    ConsoleText = translate("Dashboard", "Console")
    # for execution mode
    ExecOptimText = translate("Dashboard", "Use optimized version")
    ExecDebugText = translate("Dashboard", "Use debug version")
    ExecDebuggerText = translate("Dashboard", "Run under Debugger")
    PrepEnvText = translate("Dashboard", "Prepare the environment")

    _store = None
    # Definiton of parameters with their values that is considered as undefined.
    # They must be consistent with type declared in '.proto'
    Defs = {
        "job_type": 0,
        "casename": "",
        "assigned": False,
        "jobid": "",
        "dump_string": "",
        "name": "",
        "server": "",
        "mode": Null,
        "start_time": "",
        "end_time": "",
        "description": "",
        "studyid": "",
        "memory": 0,
        "time": "",
        "version": "",
        "mpicpu": 0,
        "nodes": 0,
        "threads": 0,
        "folder": "",
        "compress": False,
        "partition": "",
        "qos": "",
        "args": "",
        "wckey": "",
        "extra": "",
        "input_vars": [],
        "input_init": [],
        "input_bounds": [],
        "output_unit": 0,
        "output_vars": [],
        "observations_path": "",
        "execmode": "",
        "remote_folder": "",
        "language": "",
        "no_database": False,
        "make_env": False,
    }
    Commons = {
        'server': localhost_server(),
        'mode': Batch,
        'memory': 2048,
        'time': '00:15:00',
        'mpicpu': 1,
        "nodes": 1,
        'wckey': CFG.get_wckey() or '',
        'execmode': ExecOptimText,
    }
    __setattr__ = no_new_attributes(object.__setattr__)

    def __init__(self, with_default=False):
        """Initialize the instance with default values."""
        self._store = deepcopy(JobInfos.Defs)
        if with_default:
            self.add_defaults(overwrite=True)

    def copy(self):
        """Return a copy"""
        new = JobInfos()
        new.set_parameters_from(self.asdict())
        return new

    def add_defaults(self, overwrite):
        """Add common default values.

        Arguments:
            overwrite (bool): Same as in `:meth:set_parameters_from`.

        Returns:
            *JobInfos*: The object itself.
        """
        self.set_parameters_from(JobInfos.Commons, overwrite)
        return self

    @classmethod
    def valid_type(cls, key, value):
        """Check that *value* has the expected type for parameter *key*."""
        expected = [type(cls.Defs[key])]
        if expected[0] is list:
            expected.append(tuple)
        return isinstance(value, tuple(expected))

    def get(self, key):
        """Return a parameter value.

        If the parameter is not defined, its value from *Defaults* is returned.

        Arguments:
            key (str): Parameter name.

        Returns:
            misc: Parameter value. *KeyError* is raised for unknown parameters.
        """
        value = self._store[key]
        defined = self.is_defined(key)
        if not defined:
            if key == "input_init":
                value = [None] * len(self.get("input_vars"))
            elif key == "input_bounds":
                value = [[None, None]] * len(self.get("input_vars"))
        return value

    @classmethod
    def _convert(cls, key, value):
        """Convert acceptable values"""
        if value is None:
            value = cls.Defs.get(key)
        if key == "jobid" and isinstance(value, int):
            value = str(value)
        elif key == "mode" and not isinstance(value, int):
            value = JobInfos.text_to_mode(value)
        elif (key in ("memory", "mpicpu", "nodes", "threads")
              and isinstance(value, float)):
            value = int(value)
        elif key == "time" and isinstance(value, (int, float)):
            value = str(int(value))
        return value

    def set(self, key, value):
        """Set the value of a parameter.
        *KeyError* is raised for unknown parameters.

        Arguments:
            key (str): Parameter name.
            value (misc): Parameter value.
        """
        value = self._convert(key, value)
        if key not in JobInfos.Defs:
            raise KeyError("unknown parameter: {0!r}".format(key))
        if not self.valid_type(key, value):
            raise TypeError(
                "for {2!r}, expecting type: {0!r}, not {1!r}".format(
                    type(JobInfos.Defs[key]), type(value), key))
        if key == "job_type":
            if value not in (JobInfos.Aster, JobInfos.Persalys, JobInfos.Adao):
                raise ValueError('unexpected value: {0}'.format(value))
        elif key == "input_init":
            if len(value) != len(self.get("input_vars")):
                raise ValueError('expecting {0} values, not {1}'.format(
                    len(self.get("input_vars")), value))
        elif key == "input_bounds":
            if len(value) != len(self.get("input_vars")):
                raise ValueError('expecting {0} values, not {1}'.format(
                    len(self.get("input_vars")), value))
            for bounds in value:
                if not isinstance(bounds, (list, tuple)) or len(bounds) != 2:
                    raise ValueError("expecting a list of 2 values")
        self._store[key] = value

    def is_defined(self, key):
        """Tell if the parameter has been defined."""
        return self._store[key] != JobInfos.Defs[key]

    def use_aster(self):
        """Tell if the parameters are related to a code_aster execution.

        Returns:
            bool: *True* for code_aster jobs.
        """
        return self.get("job_type") == JobInfos.Aster

    def use_persalys(self):
        """Tell if the parameters are related to Persalys.

        Returns:
            bool: *True* if the target module is Persalys.
        """
        return self.get("job_type") == JobInfos.Persalys

    def use_adao(self):
        """Tell if the parameters are related to Adao.

        Returns:
            bool: *True* if the target module is Adao.
        """
        return self.get("job_type") == JobInfos.Adao

    def __eq__(self, other):
        """Tell if `self` and `other` have the same content"""
        for attr in JobInfos.Defs:
            if self.use_aster() and attr in ("input_vars", "input_init",
                                             "input_bounds", "output_unit",
                                             "output_vars",
                                             "observations_path"):
                continue
            if self.use_persalys() and attr in ("input_init", "input_bounds",
                                                "observations_path"):
                continue
            if self.get(attr) != other.get(attr):
                return False
        return True

    # Properties
    @property
    def jobid(self):
        """str: Attribute that holds the job's identifier."""
        return self.get("jobid")

    @jobid.setter
    def jobid(self, value):
        """Assign the job identifier."""
        self.set("jobid", value)
        self.set("assigned", True)

    def reload_jobid(self, value):
        """Initialize the job identifier during reloading.

        Arguments:
            value (int|str): Value of the job identifier.
        """
        self.set("jobid", str(value))

    @property
    def assigned(self):
        """bool: Tells if the "jobid" has just been reloaded or assigned."""
        return self.get("assigned")

    @property
    def jobid_int(self):
        """int: Return the job's identifier as int (for runners that expect
        an integer)."""
        return int(self.get("jobid") or -1)

    @property
    def dump_string(self):
        """str: Attribute that holds the 'dump_str' property."""
        return self.get("dump_string")

    @dump_string.setter
    def dump_string(self, value):
        self.set("dump_string", value)

    @property
    def studyid(self):
        """str: Attribute that holds the process identifier."""
        return self.get("studyid")

    @studyid.setter
    def studyid(self, value):
        """Assign the process identifier."""
        self.set("studyid", value)

    @property
    def name(self):
        """str: Attribute that holds the job's name."""
        return self.get("name")

    @name.setter
    def name(self, value):
        """Assign the jobs's name."""
        self.set("name", value)

    @property
    def server(self):
        """str: Attribute that holds the server on which the job was
        submitted."""
        return self.get("server")

    @server.setter
    def server(self, value):
        """Assign the submission server."""
        self.set("server", value)

    @property
    def mode(self):
        """int: Attribute that holds the running mode."""
        return self.get("mode")

    @mode.setter
    def mode(self, value):
        """Assign the running mode."""
        self.set("mode", value)

    @property
    def description(self):
        """str: Attribute that holds the job's description."""
        return self.get("description")

    @description.setter
    def description(self, value):
        """Assign the job description."""
        self.set("description", value)

    @property
    def start_time(self):
        """str: Attribute that holds the time when the job was submitted."""
        return self.get("start_time")

    @start_time.setter
    def start_time(self, value):
        """Set the start time."""
        self.set("start_time", value)

    @property
    def end_time(self):
        """str: Attribute that holds the time when the job was submitted."""
        return self.get("end_time")

    @end_time.setter
    def end_time(self, value):
        """Set the end time."""
        self.set("end_time", value)

    @property
    def full_description(self):
        """str: The job's description that is the description entered by the
        user and a summary of job's execution parameters."""
        ident = " " * 4
        lines = [
            self.get("description"), "",
            translate("Dashboard",
                      "Start time: {0}").format(self.get("start_time")),
            translate("Dashboard",
                      "End time: {0}").format(self.get("end_time")),
            translate("Dashboard",
                      "Server name: {0}").format(self.get("server")),
            translate("Dashboard", "Version: {0}").format(self.get("version")),
            translate("Dashboard", "Submission parameters:"),
            ident + translate("Dashboard", "Memory limit: {0} MB").format(
                self.get("memory")), ident +
            translate("Dashboard", "Time limit: {0}").format(self.get("time")),
            ident + translate("Dashboard", "Partition: {0}").format(
                self.get("partition")), ident +
            translate("Dashboard", "QOS: {0}").format(self.get("qos")),
            ident + translate("Dashboard", "Job identifier: {0}").format(
                self.get("jobid")),
            translate("Dashboard", "Parallel parameters:"), ident + translate(
                "Dashboard", "Number of nodes: {0}").format(self.get("nodes")),
            ident + translate("Dashboard", "Number of processors: {0}").format(
                self.get("mpicpu")),
            ident + translate("Dashboard", "Number of threads: {0}").format(
                self.get("threads")), ""
        ]
        return "\n".join(lines)

    @staticmethod
    def text_to_mode(text):
        """Return the text for a given mode."""
        return {
            "": JobInfos.Null,
            JobInfos.BatchText: JobInfos.Batch,
            JobInfos.InteractiveText: JobInfos.Interactive,
            JobInfos.ConsoleText: JobInfos.Console,
        }[text]

    @staticmethod
    def mode_to_text(mode):
        """Return the mode for a given text label."""
        return {
            JobInfos.Null: "",
            JobInfos.Batch: JobInfos.BatchText,
            JobInfos.Interactive: JobInfos.InteractiveText,
            JobInfos.Console: JobInfos.ConsoleText,
        }[mode]

    def set_parameters_from(self, parameters, overwrite=True):
        """Set the value of parameters from a dict.

        Arguments:
            parameters (dict): Mapping of parameters/values.
            overwrite (bool): If *False*, the parameter is only inserted if it
                is not yet defined (*True* by default).
        """
        for key in JobInfos.Defs:
            if key not in parameters.keys():
                continue
            if not overwrite and self.is_defined(key):
                continue
            self.set(key, parameters[key])

    def copy_parameters_from(self, other):
        """Copy the value of undefined parameters from another JobInfos object."""
        for key in JobInfos.Defs:
            if not self.is_defined(key) and other.is_defined(key):
                self.set(key, other.get(key))

    def asdict(self, undefined=False):
        """Return parameters as a dict.

        Arguments:
            undefined (bool): Set to *True* to also export undefined parameters

        Returns:
            dict: Dict object containing the parameters values.
        """
        params = {}
        for key in JobInfos.Defs:
            if undefined or self.is_defined(key):
                params[key] = self.get(key)
        return params

    def is_empty(self):
        """Tell if no parameter has been defined.

        Returns:
            bool: *False* if at least one parameter is set. *True* otherwise.
        """
        return not bool(self.asdict())
