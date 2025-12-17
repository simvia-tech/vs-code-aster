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
Parametric study
----------------

Implementation of the functions to deal with parametric studies.
"""

import os
import os.path as osp
from collections import namedtuple
from string import Template
from subprocess import call

from ..common import CFG, copy_file, debug_message
from .engine.engine_utils import ExportCase

try:
    # from adao import adaoBuilder
    HAS_ADAO = True
except ImportError: # pragma: no cover
    HAS_ADAO = False


INPUTS = 'inputs.pick'
OUTPUTS = 'outputs.npy'

OTData = namedtuple('OTData', ('code', 'files', 'parameters'))


class PercentTemplate(Template):
    """Template that uses '%' as fields identifier."""
    delimiter = "%"


def output_commands(case):
    """Search for commands that create output results for parametric studies.

    Arguments:
        case (Case): Case to search in.

    Returns:
        list[Command]: List of commands that match the criteria.
    """

    def _check_cmd(_cmd):
        _unit = _cmd.storage.get('UNITE')
        return (_cmd.title == 'IMPR_TABLE' and _unit is not None
                and _cmd.stage.handle2file(_unit) is not None
                and _cmd.storage.get('FORMAT') == 'NUMPY'
                and len(_cmd.storage.get(('NOM_PARA'), ())) > 0)

    found = []
    for stage in case.stages:
        found.extend([i for i in stage.sorted_commands if _check_cmd(i)])
    return found


def create_exec_function(folder, job_infos, keep_results):
    """Create the 'exec' function for parametric study.

    Arguments:
        folder (str): Path to the destination directory (must contain the
            related export file named 'parametric.export').
        job_infos (*JobInfos*): Job informations.
        keep_results (bool): if *True*, all results are copied in the
            'analysis.results' subdirectory.

    Returns:
        str: Code of the function.
    """
    template = \
"""

def _exec({input_vars}):
    import inspect
    import os
    from getpass import getuser
    from asterstudy.api import ParametricCalculation

    calc = ParametricCalculation("{folder}",
                                 [{input_names}], [{input_vars}],
                                 keep_results={keep_results})
    calc.set_logger(print)
    calc.setup()
    # following parameters are set in the 'parametric.export' file
    # but can be overridden here:
    calc.use(version="{para[version]}",
             memory={para[memory]},
             time="{para[time]}",
             mpicpu={para[mpicpu]},
             nodes={para[nodes]},
             threads={para[threads]},
             language="{para[language]}",
             args="{para[args]}")
    kwargs = dict(use_cache={keep_results})
    compat = "use_cache" not in inspect.signature(calc.run).parameters
    if compat:
        kwargs.pop('use_cache')
    calc.run(**kwargs)
    results = calc.output_values()
    if len(results) != {len_output_vars}:
        calc.log("ERROR: See log files:", calc.logfiles())
        calc.log("ERROR: results =", results)
        runc = calc.run_case_name()
        arch = "/tmp/" + getuser() + runc + ".tar"
        os.system("tar cvf {{0}} {{1}}".format(arch, runc))
        calc.log("ERROR: Directory saved as " + arch)
        raise ValueError("Calculation failed with inputs: {{0}}"
                         .format(({input_vars})))

    {output_vars} = results{first}
    return {output_vars}
"""
    appli = os.environ.get("SALOMEPATH", os.getenv("KERNEL_ROOT_DIR"))
    salome_bin = "salome"
    if appli:
        salome_bin = osp.join(appli, "salome")
    values = {
        'folder': ".",
        'para': job_infos.asdict(undefined=True),
        'input_vars': ", ".join(job_infos.get("input_vars")),
        'input_names': ", ".join(["'{0}'".format(i)
                                  for i in job_infos.get("input_vars")]),
        'output_vars': ", ".join(job_infos.get("output_vars")),
        'output_names': ", ".join(["'{0}'".format(i)
                                   for i in job_infos.get("output_vars")]),
        "len_output_vars": len(job_infos.get("output_vars")),
        'first': "" if len(job_infos.get("output_vars")) > 1 else "[0]",
        'salome_bin': salome_bin,
        'keep_results': repr(keep_results),
    }
    code = template.format(**values)
    with open(osp.join(folder, 'parametric.code'), 'w') as fcode:
        fcode.write(code)

    if job_infos.use_adao():
        values['code'] = code
        create_adao_files(folder, job_infos, values)
    return code


def create_adao_files(folder, job_infos, values):
    """Create files needed by Adao.

    Arguments:
        folder (str): Path to the parametric case directory.
        job_infos (*JobInfos*): Job informations.
        values (dict): Template data.
    """
    values.update({
        'code': values['code'],
        'input_initial': job_infos.get("input_init"),
        'input_bounds': job_infos.get("input_bounds"),
        'observations': repr("observations.csv"),
    })
    for fname in ('adao_go.sh', 'adao_data.py'):
        ftmpl = osp.join(CFG.rcdir, "parametric", fname)
        with open(ftmpl, "r") as fobj:
            template = PercentTemplate(fobj.read())
        text = template.substitute(values)
        with open(osp.join(folder, fname), "w") as fobj:
            fobj.write(text)
    os.chmod(osp.join(folder, 'adao_go.sh'), 0o755)
    copy_file(job_infos.get("observations_path"),
              osp.join(folder, "observations.csv"))
    for fname in ('adao_script.comm', 'adao_script.py', 'adao_post.py'):
        copy_file(osp.join(CFG.rcdir, "parametric", fname),
                  osp.join(folder, fname))
    create_adao_xml(folder, 'adao_script.xml')


def create_adao_xml(folder, xml):
    """Create YACS XML schema from Adao commands file (.comm or .py) and
    required data files.

    Arguments:
        xml (str): Output Yacs XML schema.
    """
    # waiting for bug fix in generator
    assert HAS_ADAO, "ADAO module is required for this feature!"
    # case = adaoBuilder.New()
    # case.convert(FileNameFrom="adao_script.comm", FormaterFrom="COM",
    #              FileNameTo=xml, FormaterTo="YACS")
    # del case
    assert os.getenv("ADAO_ENGINE_ROOT_DIR")
    creator = osp.join(os.environ["ADAO_ENGINE_ROOT_DIR"], "bin",
                       "AdaoYacsSchemaCreator.py")
    cmd = ["python", creator, "adao_script.py", xml]
    debug_message("Executing:", " ".join(cmd))
    retcode = call(cmd, cwd=folder)
    assert retcode == 0, retcode
    assert osp.isfile(osp.join(folder, xml))


def export_to_parametric(case, folder, keep_results=True):
    """Export the case for parametric study.

    Arguments:
        case (Case): Case to search in.
        folder (str): Path to the directory to write files in.
        keep_results (bool, optional): if *True*, all results are copied in the
            'analysis.results' subdirectory.

    Return:
        *OTData*: NamedTuple containing: '.code': code of the function,
        '.files': input files, '.parameters': dict of the job parameters.
    """
    unit = case.job_infos.get("output_unit")
    info = None
    stage_number = 0
    for stage in case.stages:
        if unit in stage.handle2info:
            info = stage.handle2info[unit]
            stage_number = stage.number
            break
    # set the expected filename
    if info is None:
        return OTData("", [], {})
    bckp = info.filename
    info.filename = OUTPUTS

    export_name = osp.join(folder, "parametric.export")
    export = ExportCase.factory(case, export_name, parametric=True)
    export.set_last_stage(stage_number)
    export.generate()
    files = [
        osp.join(folder, path) for path in export.get_input_files()
        if path != INPUTS
    ]
    files.append(export_name)

    # restore original path
    info.filename = bckp

    code = create_exec_function(folder, case.job_infos, keep_results)

    return OTData(code, files, case.job_infos.asdict())
