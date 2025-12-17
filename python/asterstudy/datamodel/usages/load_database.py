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
Load Database
-------------

Implementation of the initialization of a Case from an already existing
database. A RunCase is created and executed to reload the database.
The contained concepts are extracted from this execution to be available
to continue the data settings with a graphical stage.

Finally, a RunCase is completed to allow continuation.
"""


import os
import re

from ..catalogs import CATA
from ..engine.helper import CalcWatcher
from ..job_informations import JobInfos
from ..result import StateOptions as SO
from ..stage import UsageOptions

LOAD_DATABASE = """

POURSUITE()

try:
    from code_aster import DataStructure as DS
except ImportError:
    from code_aster.Cata.Syntax import ASSD as DS

loaded = list(globals().items())
for name, obj in loaded:
    if isinstance(obj, DS):
        if hasattr(obj, 'getType'):
            typ = obj.getType()
        else:
            typ = obj.__class__.__name__
        print("LoadDataBase:{0},{1}".format(name, typ))

del loaded

FIN()
"""

def load_database(history, path, extract=True, engine=None, job_infos=None):
    """Create a RunCase loading a database.

    Arguments:
        history (History): Main object.
        path (str): Path to the database.
        engine (*Engine*, optional): Engine type, only for unittest.
        job_infos (*JobInfos*, optional): Job parameters.
    """
    history.create_case(replace=True)

    current = history.current_case
    init_stg = create_stage_from_database(current, path)

    if not extract:
        return current

    new_name = history.new_run_case_name("LoadDataBaseInit")
    init_case = history.create_run_case(name=new_name)
    jinf = init_case.job_infos
    jinf.add_defaults(overwrite=False)
    jinf.set('version', history.version)
    jinf.set_parameters_from((job_infos or JobInfos).asdict())

    watch = CalcWatcher()
    watch.run_case = init_case
    watch.set_engine(engine)
    watch.run()

    if not watch.state & SO.Success: # pragma: no cover
        return current

    output = init_stg.output_file()
    with open(output) as fout:
        text = fout.read()

    filt = re.compile('^LoadDataBase:(.*),(.*) *$', re.M)
    objects = filt.findall(text)
    keep_dir = init_case.folder
    os.rename(keep_dir, keep_dir + ".saved")
    init_case.delete()
    init_stg.delete()

    stage = create_stage_from_database(current, path)
    _define_concepts(stage, objects)

    new_name = history.new_run_case_name("LoadDataBase")
    load = history.create_run_case(name=new_name)
    stage.result.state = SO.Success
    os.rename(keep_dir + ".saved", load.folder)

    # copy as current
    current.copy_from(load)
    return current


def create_stage_from_database(case, path):
    """Create a stage that loads a database."""
    stage = case.create_stage("Initialization")
    stage.use_text_mode()
    stage.set_text(LOAD_DATABASE)
    stage.usage = UsageOptions.LoadDatabase
    stage.database = path
    return stage

def _define_concepts(stage, objects):
    typ2cmd = CATA.type2command
    defs = []
    for obj, typ in objects:
        typ = typ.lower()
        defs.append([obj, typ2cmd[typ].name, typ])

    stage.update_commands(defs)
