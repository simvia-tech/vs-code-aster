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
Convert Mesh
------------

Implementation of a service that converts
"""


import os.path as osp
import tempfile

from ...common import get_extension, translate


class MeshConverter:
    """This implements the conversion of a mesh file in order to be used
    as a SMesh object.
    """

EXTENSIONS = {
    "mail": "mail",
    "msh": "gmsh",
    "msup": "ideas",
    "unv": "ideas",
    "mgib": "gibi",
}

FORMAT = {'mail': 'ASTER', 'gmsh': 'GMSH', 'gibi': 'GIBI', 'ideas': 'IDEAS'}

CONVERT = """
{name} = LIRE_MAILLAGE(FORMAT="{fmt}", UNITE=2)
IMPR_RESU(FORMAT="MED", UNITE=3, RESU=_F(MAILLAGE={name}))
"""


def convert_mesh(path, format=None, mesh_name="mesh", log=print):
    """Convert a mesh file.

    Arguments:
        path (str): Path of the mesh file.

    Returns:
        str: Path to the med file.
    """
    from ...api import Calculation, FileAttr, StateOptions

    fmt = FORMAT.get(format or get_extension(path))
    if not fmt:
        log(translate("AsterStudy",
                      "Unknown mesh format for: {0}".format(path)))
        return None

    tmpdir = tempfile.mkdtemp(prefix="convmesh_")
    log(translate("AsterStudy",
                  "Starting mesh conversion in directory {0}...")
        .format(tmpdir))
    calc = Calculation(tmpdir)
    calc.add_stage_from_string(CONVERT.format(fmt=fmt, name=mesh_name))
    calc.add_file(path, 2, FileAttr.In)
    medfile = tempfile.mkstemp(suffix=".med")[1]
    calc.add_file(medfile, 3, FileAttr.Out)
    calc.run()
    log(translate("AsterStudy",
                  "Conversion ended with state {0}")
        .format(calc.state_name))

    if calc.state & StateOptions.Success and osp.isfile(medfile):
        calc.delete_files()
    else:
        for filename in calc.logfiles():
            log("ERROR: mesh conversion failed, see", filename)
        raise RuntimeError(translate("AsterStudy",
                                     "Conversion ended with state {0}")
                           .format(calc.state_name))
    return medfile
