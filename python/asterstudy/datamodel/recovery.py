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
Recovery feature
----------------

Implementation of the recovery from corrupted study.

"""

import json
import os.path as osp

from ..common import is_reference


def recovery_json(case, json_dict):
    """
    Recover the history content from a JSON dict.

    Arguments:
        case (Case): Destination *Case* object.
        json (dict): Data as a JSON dict.
    """
    rhist = json_dict['history']
    rcase = rhist['cases'][-1]
    stgids = rcase['stages']
    rstages = [stg for stg in rhist['stages'] if stg['uid'] in stgids]

    for rstage in rstages:
        stg = case.text2stage(rstage['text'], rstage['name'])
        for rinfo in rstage.get('files', []):
            unit = rinfo['handle']
            filename = rinfo['filename']
            if osp.exists(filename) or is_reference(filename):
                info = stg.handle2info[unit]
                info.filename = filename
                info.attr = rinfo['attr']


def recover_from_ajs(case, filename):
    """
    Import the JSON content in the current case.

    Arguments:
        case (Case): Destination *Case* object.
        filename (str): Path to the ".ajs" file to be read.
    """
    recovery_json(case, _load_json(filename))


def get_version_from_ajs(filename):
    """
    Extract the version name from a ".ajs" file.

    Arguments:
        filename (str): Path to the ".ajs" file to be read.

    Returns:
        str: Version name.
    """
    json_dict = _load_json(filename)
    return json_dict['history']['aster']


def _load_json(filename):
    """Load a JSON file.

    Arguments:
        filename (str): Path to the ".ajs" file to be read.

    Returns:
        dict: JSON dict.
    """
    with open(filename, 'rb') as ajs:
        json_dict = json.load(ajs)
    return json_dict
