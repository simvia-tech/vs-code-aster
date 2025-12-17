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
Yacs runner
-----------

This module defines a runner to execute a Yacs schema following the execution
in the Dashboard.

It is currently only used for Adao. So, the extraction of job informations
should be in a dedicated class if used for other purposes.

"""

import os.path as osp
import re

from ...common import (CFG, RunnerError, current_time, info_message,
                       to_unicode, translate, valid_file_name)
from ..parametric import export_to_parametric
from ..result import StateOptions as SO
from .edf_servers import adapt_parameters
from .salome_runner import (Salome, SalomeInfos, new_directory,
                            resource_parameters)

try:
    import salome
    salome.salome_init()
    HAS_SALOME = True
except (ImportError, RuntimeError):  # pragma: no cover
    HAS_SALOME = False


class Yacs(Salome):
    """Runner to execute a Yacs schema using JobLauncher of SALOME.

    Arguments:
        case, logger: see
            :obj:`datamodel.engine.abstract_runner.Runner`.
    """
    watched_file = osp.join("logs", "[0-9]*_*Container_*.log")

    def start_current(self):
        """Activate calculation simulation for next result."""
        stage = self.current_stage
        stagename = self._name(stage)
        name = valid_file_name(stagename)
        self.log(translate('Runner', 'Starting "{0}"...').format(stagename))
        job_infos = self._case.job_infos
        try:
            server = job_infos.get('server')
            servcfg = self._infos.server_config(server)
            if not servcfg:
                raise RunnerError(
                    translate("Runner",
                              "Server {0!r} is not available.").format(server))

            salome_job = create_yacs_job(servcfg, self._case, stage.folder)
            if job_infos.get("make_env") and job_infos.use_adao():
                self.current.state = SO.Pending
                job_infos.name = name
                job_infos.start_time = current_time()
                self.log(
                    translate(
                        'Runner',
                        'Calculation not started, execution directory prepared'
                    ))
                return
            jobid = self.hdlr.createJob(salome_job)
            try:
                # TODO copy remote input files in salome workdir
                info_message("Submitting job on {0}...".format(server))
                self.hdlr.launchJob(jobid)
                info_message("job submitted")
            except Exception as exc:
                msg = translate(
                    'Runner',
                    'Error during submission of "{0}"'.format(stagename))
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
            # job_infos.studyid = prof['studyid'][0]
            job_infos.jobid = str(jobid)
            job_infos.name = name
            job_infos.start_time = current_time()
            job_infos.dump_string = self.hdlr.dumpJob(jobid)
            self.log(
                translate('Runner',
                          'Stage "{0}" start calculation (jobid={1})').format(
                              stagename, jobid))

    def _update_state_from_output(self, output, launcher_state, console=False):
        """"Update the "launcher" state from the output.

        Arguments:
            output (str): Output filename.
            launcher_state (int): *JobLauncher* job state.
            console (bool, optional): *True* if the job was executed through a
                terminal.
        """
        re_error = re.compile("(error|aborted|killed)", re.I | re.M)
        with open(output, 'rb') as fileout:
            text = to_unicode(fileout.read())
            # self.current.clear_messages()
            # self.current.add_messages(extract_messages(text))
            error = re_error.search(text) is not None
            info_message("Error found in the Yacs log file" if error else
                         "Analysis results are available in the Yacs log file")
            self.current.state = SO.Error if error else self.current.state

    def _copy_results(self):
        """Do not copy results files for Adao"""
        return 0


class YacsInfos(SalomeInfos):
    """Class that provides informations of the servers."""


def create_yacs_job(servcfg, case, folder):
    """Create the SalomeLauncher job."""
    # case.make_run_dir()
    jinf = case.job_infos
    data = export_to_parametric(case, folder, keep_results=True)

    salome_job = salome.JobParameters()
    salome_job.job_name = "adao_script"
    salome_job.job_type = "yacs_file"
    salome_job.wckey = jinf.get('wckey') or CFG.get_wckey() or ''
    salome_job.job_file = osp.join(folder, "adao_script.xml")
    salome_job.result_directory = folder
    salome_job.work_directory = new_directory(servcfg)
    salome_job.maximum_duration = jinf.get('time')
    salome_job.extra_params = jinf.get('extra')

    adapt_parameters(salome_job, jinf)

    # Provided in files will be copied by Launcher onto execution dir
    #     (remote if necessary)
    in_files = [
        osp.join(folder, name)
        for name in ("adao_data.py", "adao_post.py", "observations.csv")
    ]
    in_files.extend(data.files)
    salome_job.in_files = in_files

    # Only basenames are provided to the launcher for out files
    salome_job.out_files = ["analysis.npy", "analysis.txt", "analysis.results"]
    salome_job.resource_required = resource_parameters(jinf)

    return salome_job
