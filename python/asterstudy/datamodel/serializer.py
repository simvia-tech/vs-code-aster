#!/usr/bin/env python
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
Persistence
-----------

AsterStudy related serialization functionality

"""

import os
import traceback

import numpy

from google.protobuf import json_format

from ..common import ConversionError, VersionError, debug_message, info_message
from ..common.version import (VERSION_DB_MAJOR, VERSION_DB_MINOR,
                              VERSION_DB_PATCH)
from . import asterstudy_pb2
from .backup import BackupHistory
from .dataset import DataSet
from .general import ConversionLevel
from .job_informations import JobInfos

STRICT_DEFAULT = ConversionLevel.Any

__test__ = int(os.getenv("ASTERSTUDY_WITHIN_TESTS", "0"))


def factory(file_name, serializer=None, strict=None):
    "Returns a proper serializer instance"
    extension = os.path.splitext(file_name)[1][1:]
    if extension == 'ast':
        return serializer

    strict = STRICT_DEFAULT if strict is None else strict
    return JSONSerializer(strict)


class JSONSerializer:
    """
    Simple serializer object based on Python `pickle` functionality.

    Args:
        strict (ConversionLevel): If False, loading does not fail if graphical
            stages can not be reloaded, use text dataset instead.
            Defaults to *STRICT_DEFAULT*.
    """

    def __init__(self, strict=STRICT_DEFAULT):
        self._strict = strict

    def save(self, history, file_name):  # pragma pylint: disable=no-self-use
        """
        Save model.

        Arguments:
            model (AbstractDataModel): Model object.
            file_name (str): Path to the file.
        """
        js_text = history2json(history)

        with open(file_name, "w") as handle:
            handle.write(js_text)
            handle.flush()

    def load(self, file_name, class_, **kwargs):
        """
        Load model.

        Arguments:
            file_name (str): Path to the file.
            class_ (type): Should be *History*.
            kwargs (Optional): Keywords arguments passed to create the History.

        Returns:
            AbstractDataModel: Model object.
        """
        # passing History as target class avoid recursive import
        with open(file_name) as handle:
            js_text = handle.read()

            history = json2history(js_text,
                                   class_,
                                   strict=self._strict,
                                   **kwargs)

        return history


def history2document(history):  # pragma pylint: disable=too-many-locals
    "Converts History instance to AsterStudy ProtoBuffer message"
    bdocument = asterstudy_pb2.BDocument()

    bdocument.major = VERSION_DB_MAJOR
    bdocument.minor = VERSION_DB_MINOR
    bdocument.patch = VERSION_DB_PATCH

    backup = BackupHistory()
    bhistory = bdocument.history  # pragma pylint: disable=no-member
    bhistory.aster = history.version
    bhistory.versionMajor, bhistory.versionMinor, bhistory.versionPatch = \
        history.version_number
    bhistory.remote_folder_base = history.remote_folder_base or ''

    suids = set()
    stage2uid = {}
    for case in history:
        info_message("saving case {0.uid}-{0.name}...".format(case))
        bcase = bhistory.cases.add()
        bcase.name = case.name
        bcase.base_folder = case.base_folder
        bcase.description = case.description
        bcase.is_backup = case.is_backup
        bcase.in_dir = case.in_dir if case.in_dir else ''
        bcase.out_dir = case.out_dir if case.out_dir else ''

        _save_job_infos(bcase.job_infos, case.job_infos)

        for stage in case:
            if stage not in stage2uid:
                debug_message("saving stage {0.uid}-{0.name}...".format(stage))
                bstage = bhistory.stages.add()
                bstage.name = stage.name
                bstage.mode = stage.saving_mode
                text = stage.get_text(sort=True,
                                      pretty=False,
                                      pretty_text=False)
                bstage.text = text
                backup.save_stage(stage, text)
                bstage.base_folder = stage.base_folder
                if stage.saving_mode == DataSet.textMode:
                    for cmd in stage.commands:
                        if cmd.name != "_":
                            bcommand = bstage.cmd_defs.add()
                            bcommand.name = cmd.name
                            bcommand.title = cmd.title
                            bcommand.type = cmd.printable_type
                        for i in cmd.deletes():
                            bstage.cmd_dels.append(i.name)

                for handle, info in stage.handle2info.items():
                    binfo = bstage.files.add()
                    binfo.handle = handle

                    binfo.attr = info.attr
                    binfo.embedded = info.embedded

                    filename = info.filename
                    if filename is None:
                        continue

                    binfo.filename = filename
                    backup.add_file(filename, handle, info.attr)

                bresult = bstage.result
                bresult.resstate = stage.result.state
                bresult.has_remote = stage.result.has_remote

                suids.add(stage.uid)
                uid = len(suids)
                bstage.uid = uid
                stage2uid[stage] = uid
            bcase.stages.append(stage2uid[stage])
    backup.end()

    return bdocument


def document2history(bdocument,
                     class_,
                     strict=STRICT_DEFAULT,
                     aster_version=None):
    """Converts AsterStudy ProtoBuffer message to History instance

    Arguments:
        bdocument (BDocument): AsterStudy ProtoBuffer document.
        class_ (type): *History* class.
        strict (Optional[ConversionLevel]): Tells how strict the conversion
            must be.
        aster_version (Optional[str]): code_aster version used instead of those
            stored in the document.
    """
    # pragma pylint: disable=too-many-locals
    bhistory = bdocument.history
    history = class_(
        bhistory.aster if aster_version is None else aster_version)
    history.remote_folder_base = bhistory.remote_folder_base
    snumb = ".".join([str(i) for i in history.version_number])
    info_message("Use version '{0}' ({1})".format(history.version, snumb))
    bvers = bhistory.versionMajor, bhistory.versionMinor, bhistory.versionPatch
    if bvers != history.version_number:
        sbvers = ".".join([str(i) for i in bvers])
        msgerr = ("The study was created using the '{0}' version as {1} "
                  "but the available '{0}' version is {2}").format(
                      history.version, sbvers, snumb)
        if strict & ConversionLevel.Restore:
            raise VersionError(msgerr)
        debug_message(msgerr)

    uid2stage = {}
    nbcases = len(bhistory.cases)
    for idx, bcase in enumerate(bhistory.cases):
        name = bcase.name
        if idx == 0:
            case = history.current_case
            case.name = name
        else:
            case = history.create_case(name)

        info_message("loading case {0!r} ({1}/{2})...".format(
            name, idx + 1, nbcases))
        case.base_folder = bcase.base_folder
        is_runcase = nbcases != 0 and idx != nbcases - 1

        case.description = bcase.description
        case.is_backup = bcase.is_backup
        if bcase.in_dir:
            try:
                case.in_dir = bcase.in_dir
            except ValueError as exc:
                info_message("Can not set input directory:", str(exc))
        if bcase.out_dir:
            try:
                case.out_dir = bcase.out_dir
            except ValueError as exc:
                info_message("Can not set output directory:", str(exc))

        jinf = _load_job_infos(bcase)
        case.job_infos = jinf
        bck_compat_infos = None

        info_message("loading stages...")
        for stageid in bcase.stages:
            if stageid in uid2stage:
                stage = uid2stage[stageid]
                case.add_stage(stage)
                _check_stage_mode(stage, is_runcase, strict)
            else:
                bstage = bhistory.stages[stageid - 1]

                debug_message(
                    "loading stage {0.uid}-{0.name}...".format(bstage))
                stage = case.create_stage(bstage.name)
                text = bstage.text
                stage.use_text_mode()
                stage.set_text(text)
                stage.base_folder = bstage.base_folder

                stage.saving_mode = bstage.mode
                _check_stage_mode(stage, is_runcase, strict)

                if stage.saving_mode == DataSet.textMode:
                    defs = [(i.name, i.title, i.type) for i in bstage.cmd_defs]
                    stage.update_commands(defs)
                    stage.delete_commands(bstage.cmd_dels)

                for binfo in bstage.files:
                    info = stage.handle2info[binfo.handle]

                    info.attr = binfo.attr
                    info.embedded = binfo.embedded

                    filename = binfo.filename
                    if filename == '':
                        continue

                    info.filename = filename

                bresult = bstage.result
                # backward compatibility: resstate[int] replaces state[enum]
                if not bresult.resstate and bresult.state:
                    bresult.resstate = bresult.state
                stage.result.state = bresult.resstate
                stage.result.has_remote = bool(bresult.has_remote)
                # backward compatibility - only keep the last read
                bck_compat_infos = init_from_bjob(bresult.job)

                uid2stage[stageid] = stage
        _compatibility_load(bck_compat_infos, history, case, bcase)
        info_message("case {0!r} loaded".format(name))
    return history


def _check_stage_mode(stage, is_runcase, strict):
    """Check the Stage mode:

    - If the *ConversionLevel* forces to text, keep the stage as pure text.

    - If the stage belongs to a *RunCase*, let the stage in text mode and
      remember that it had been saved as a graphical stage.

    - Else if the stage had been saved as a graphical stage and belongs to
      the *CurrentCase*, it is converted to graphical mode.
    """
    mode = stage.saving_mode
    debug_message("stage saved in mode:", "text" if mode else "graphical")
    if strict & ConversionLevel.NoGraphical:
        mode = DataSet.textMode
        stage.saving_mode = mode

    if is_runcase:
        mode = DataSet.textMode
        debug_message("in a runcase => text")

    if mode == DataSet.graphicalMode:
        try:
            stage.use_graphical_mode(strict)
        except (TypeError, ConversionError):
            debug_message("conversion failed:", traceback.format_exc())
            if strict & ConversionLevel.Syntaxic:
                raise
            stage.use_text_mode()
            stage.set_text(stage.get_text(pretty_text=True))
    else:
        stage.use_text_mode()


def _save_job_infos(bjob, job_infos):
    """Fill BJob with job informations from case.

    Arguments:
        bjob (BJob): Output object to be filled.
        job_infos (JobInfos): Parametric data of the case.
    """
    for key in JobInfos.Defs:
        if not hasattr(bjob, key):
            continue
        if key in ("input_vars", "output_vars"):
            getattr(bjob, key).extend(job_infos.get(key))
        elif key == "input_init":
            for value in job_infos.get(key):
                isdef = value is not None
                getattr(bjob, key).append(float(value) if isdef else 0.)
                getattr(bjob, key + "_mask").append(isdef)
        elif key == "input_bounds":
            for value in numpy.ravel(job_infos.get(key)):
                isdef = value is not None
                getattr(bjob, key).append(float(value) if isdef else 0.)
                getattr(bjob, key + "_mask").append(isdef)
        else:
            setattr(bjob, key, job_infos.get(key))


def _load_job_infos(bcase):
    """Load BJob object.

    Arguments:
        bcase (BCase): Input case object.
    """
    bjob = bcase.job_infos
    job_infos = init_from_bjob(bjob)
    # using mask and reshape
    initial = [
        value if mask else None
        for value, mask in zip(bjob.input_init, bjob.input_init_mask)
    ]
    if initial:
        job_infos.set("input_init", initial)
    bounds = numpy.array([
        value if mask else None
        for value, mask in zip(bjob.input_bounds, bjob.input_bounds_mask)
    ])
    if bounds.size:
        job_infos.set("input_bounds", bounds.reshape(-1, 2).tolist())
    return job_infos


def init_from_bjob(bjob):
    """Initialize a JobInfos from BJob object."""
    job_infos = JobInfos()
    for key, default in JobInfos.Defs.items():
        if getattr(bjob, key, None) is None:
            continue
        if key == "jobid":
            job_infos.reload_jobid(bjob.jobid)
            continue
        if key in ("input_init", "input_bounds"):
            continue
        job_infos.set(key, type(default)(getattr(bjob, key)))
    return job_infos


def _compatibility_load(compat, history, case, bcase):
    """Support backward compatibility"""
    jinf = case.job_infos
    if jinf.is_empty() and compat:
        jinf.copy_parameters_from(compat)
    # backward compatibility
    if bcase.ot_vars or bcase.ot_cmd:
        jinf.set("job_type", JobInfos.Persalys)
        if bcase.ot_vars:
            jinf.set("input_vars", bcase.ot_vars.split(','))
        if bcase.ot_cmd:
            cmd = history.get_node(bcase.ot_cmd)
            if cmd:
                jinf.set("output_unit", cmd.storage.get('UNITE') or 0)


def document2json(bdocument):
    "Converts AsterStudy ProtoBuffer message to JSON text representation"
    js_text = json_format.MessageToJson(bdocument)

    return js_text


def json2document(js_text):
    "Converts JSON text representation to AsterStudy ProtoBuffer message"
    bdocument = asterstudy_pb2.BDocument()
    json_format.Parse(js_text, bdocument)
    return bdocument


def history2json(history):
    "Converts History instance to JSON text representation"
    bdocument = history2document(history)
    js_text = document2json(bdocument)

    return js_text


def json2history(js_text, class_, strict=STRICT_DEFAULT, **kwargs):
    """Converts JSON text representation to AsterStudy History instance.

    Arguments:
        js_text (str): Content of JSON document.
        class_ (type): Destination type.
        strict (Optional[ConversionLevel]): Tells how strict the conversion
            must be.
        kwargs (Optional): Keywords arguments passed to create the History.
    """
    bdocument = json2document(js_text)
    history = document2history(bdocument, class_, strict, **kwargs)

    return history
