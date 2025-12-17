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
External files
--------------

Auxiliary utilities for external files services.

"""


import os
import re
from collections import OrderedDict

from .base_utils import get_extension, to_unicode
from .utilities import (change_cursor, debug_message, info_message, to_list,
                        translate)

__all__ = ["MeshGroupType", "MeshElemType", "FilesSupplier", "is_reference",
           "external_files", "external_file", "external_file_groups",
           "external_file_groups_by_type", "external_file_export_to_med",
           "external_files_callback", "get_medfile_meshes",
           "get_medfile_groups", "get_medfile_groups_by_type",
           "get_cmd_groups", "is_valid_group_name"]


class MeshGroupType:
    """
    Enumerator for mesh group type.

    Attributes:
        GNode: Group of nodes.
        GElement: Group of elements.
    """
    GNode = 0
    GElement = 1

    @staticmethod
    def value2str(value):
        """
        Get title for given mesh group type.

        Arguments:
            value (int): Group type (*MeshGroupType*).

        Returns:
            str: Mesh group type's title.

        Raises:
            TypeError: If invalid *value* is specified.
        """
        text = ""
        if value == MeshGroupType.GNode:
            text = translate("AsterStudy", "Nodes")
        elif value == MeshGroupType.GElement:
            text = translate("AsterStudy", "Elements")
        else:
            raise TypeError("Invalid group type: {}".format(value))
        return text


class MeshElemType:
    """
    Enumerator for mesh element type.

    Attributes:
        ENode: Nodes.
        E0D: 0D elements.
        E1D: Edges.
        E2D: Faces.
        E3D: Volumes.
    """
    ENode = -1
    E0D = 0
    E1D = 1
    E2D = 2
    E3D = 3

    EAll = 10

    @staticmethod
    def value2str(value):
        """
        Get title for given mesh element type.

        Arguments:
            value (int): Element type (*MeshElemType*).

        Returns:
            str: Mesh element type's title.

        Raises:
            TypeError: If invalid *value* is specified.
        """
        text = ""
        if value == MeshElemType.ENode:
            text = translate("AsterStudy", "Nodes")
        elif value == MeshElemType.E0D:
            text = translate("AsterStudy", "0D elements")
        elif value == MeshElemType.E1D:
            text = translate("AsterStudy", "1D elements")
        elif value == MeshElemType.E2D:
            text = translate("AsterStudy", "2D elements")
        elif value == MeshElemType.E3D:
            text = translate("AsterStudy", "3D elements")
        elif value == MeshElemType.EAll:
            text = translate("AsterStudy", "All")
        else:
            raise TypeError("Invalid element type: {}".format(value))
        return text

    @staticmethod
    def elem_types(group_type, withall=False):
        """
        Get element types for given *group_type*.

        Arguments:
            group_type (int): Group type (*MeshGroupType*).
            withall (bool): Adds an 'all' type at the beginning of the
               elements list.

        Returns:
            list[int]: List of element types (*MeshElemType*)
        """
        elem_types = [MeshElemType.E0D, MeshElemType.E1D,
                      MeshElemType.E2D, MeshElemType.E3D]
        elem_types_withall = elem_types[:]
        elem_types_withall.insert(0, MeshElemType.EAll)
        types = {
            MeshGroupType.GNode: [MeshElemType.ENode],
            MeshGroupType.GElement: elem_types_withall if withall \
                                    else elem_types
            }
        return types.get(group_type, [])

    @classmethod
    def list_elem_types(cls):
        """Returns a list with all available elementary types"""
        return cls.elem_types(MeshGroupType.GNode) + \
               cls.elem_types(MeshGroupType.GElement)


class FilesSupplier:
    """Base class for files supplier."""

    def files(self, file_format=None):
        """
        Get list of files for given format.

        This method can be redefined in successors. Default
        implementation returns empty list.

        Arguments:
            file_format (Optional[str]): File format. Defaults to
                *None*.

        Returns:
            list[str]: List of files.
        """
        # pragma pylint: disable=unused-argument,no-self-use
        return []

    def filename(self, uid):
        """
        Get file name for given reference.

        This method can be redefined in successors. Default
        implementation returns *None*.

        Arguments:
            uid (str): File *UID* (for example, reference).

        Returns:
            str: File name.
        """
        # pragma pylint: disable=unused-argument,no-self-use
        return None

    def groups(self, uid, group_type):
        """
        Get names of groups for given file.

        This method can be redefined in successors. Default
        implementation returns empty list.

        Arguments:
            uid (str): File *UID* (for example, reference).
            group_type (int): Type of mesh group (see `MeshGroupType`).

        Returns:
            list[str]: Names of groups.
        """
        # pragma pylint: disable=unused-argument,no-self-use
        return []

    def groups_by_type(self, uid, elem_type, with_size=False):
        """
        Get names of mesh groups by given element type.

        This method can be redefined in successors. Default
        implementation returns empty list.

        Arguments:
            uid (str): File *UID* (for example, reference).
            elem_type (int): Type of mesh elements (see `MeshElemType`).
            with_size (Optional[bool]): Flag specifying that sizes of groups
                should be returned as well. Defaults to *False*.

        Returns:
            list[info]: List of mesh groups' names or tuples where each
            tuple contains name of group and its size - the behavior is
            controlled by *with_size* parameter.
        """
        # pragma pylint: disable=unused-argument,no-self-use
        return []

    def export_to_med(self, uid, filepath):
        """
        Export objects to MED format.

        This method can be redefined in successors. Default
        implementation does nothing.

        Arguments:
            uid (str): indentifier of the object.
            filepath (str): path where to export the file.
        """

def is_reference(name):
    """
    Returns *True* if given *name* seems to be a reference to SALOME
    study object.

    SALOME objects can be referenced by study entry address, for
    instance "0:1:2:3".

    Example:
        >>> from asterstudy.common.extfiles import is_reference
        >>> is_reference("/aaa/bbb/ccc.txt")
        False
        >>> is_reference("0:1:2:3")
        True

    Arguments:
        name (str): Name being checked.

    Returns:
        bool: Result of check (*True* or *False*).
    """
    return re.match("^0([:][0-9]+)+$", name) is not None \
        if name is not None else False


def gen_mesh_file_name(ref, extension):
    """
    Generates a valid file basename from a SALOME entry.

    Arguments:
        ref (str): entry of the object.
        extension (str): extension for the file

    Returns:
        str: file basename.
    """
    prefix = "_ExportedFromSalomeObject_"
    return prefix + ref.replace(":", "_") + os.extsep + extension


def external_files(file_format=None):
    """
    Get external files for specified format as specified by registered
    files suppliers.

    The files suppliers are registered by means of
    `external_files_callback()` function.

    Arguments:
        file_format (str): Format string.

    Returns:
        list[str]: List of filenames.

    See also:
        `external_files_callback()`, `external_file()`
    """
    ext_files = []
    for supplier in getattr(external_files, "callbacks", []):
        ext_files += supplier.files(file_format)
    return sorted(list(set(ext_files)))


def external_file(uid):
    """
    Get external file name for given *uid*.

    External files are obtained from files suppliers which are
    registered with `external_files_callback()` function.

    Arguments:
        uid (str): File's identifier (e.g. reference).

    Returns:
        str: File name as returned by files supplier (*None* if file
        with given *uid* is not found).

    See also:
        `external_files()`, `external_files_callback()`
    """
    for supplier in getattr(external_files, "callbacks", []):
        file_name = supplier.filename(uid)
        if file_name is not None:
            return file_name
    return None


def external_file_groups(uid, group_type):
    """
    Get names of mesh groups from external files as provided by
    registered files suppliers.

    Arguments:
        uid (str): File's identifier (e.g. reference).
        group_type (int): Type of mesh group (see `MeshGroupType`).

    Returns:
        list[str]: Names of groups.
    """
    groups = []
    for supplier in getattr(external_files, "callbacks", []):
        groups += supplier.groups(uid, group_type)
    return groups


def external_file_groups_by_type(uid, elem_type, with_size=False):
    """
    Get names of mesh groups from external files as provided by
    registered files suppliers.

    Arguments:
        uid (str): File's identifier (e.g. reference).
        elem_type (int, list[int]): Type(s) of mesh elements
            (see `MeshElemType`).
        with_size (Optional[bool]): Flag specifying that sizes of groups
            should be returned as well. Defaults to *False*.

    Returns:
        list[info]: List of mesh groups' names or tuples where each
        tuple contains name of group and its size - the behavior is
        controlled by *with_size* parameter.
    """
    groups = []
    elem_types = to_list(elem_type)
    for supplier in getattr(external_files, "callbacks", []):
        for typ in elem_types:
            groups += supplier.groups_by_type(uid, typ, with_size)
    return groups

def external_file_export_to_med(uid, filepath):
    """
    Export meshes objects as provided by registered files suppliers to MED.

    Arguments:
        uid (str): File's identifier (e.g. reference).
        filepath (int): Path where to export the mesh.
    """
    for supplier in getattr(external_files, "callbacks", []):
        supplier.export_to_med(uid, filepath)

def external_files_callback(supplier, is_on):
    """
    Register / unregister files supplier.

    Arguments:
        supplier (FilesSupplier): Files supplier.
        is_on (bool): Action: *True* - register supplier,
            *False* - unregister supplier.

    See also:
        `external_files()`, `external_file()`
    """
    if not hasattr(external_files, "callbacks") and is_on:
        external_files.callbacks = []

    suppliers = external_files.callbacks

    if is_on and supplier not in suppliers:
        suppliers.append(supplier)
    elif not is_on and supplier in suppliers:
        suppliers.remove(supplier)

def is_medfile(file_name):
    """
    Check if a file is a medfile
    Note:
        The function uses MedCoupling library's Python API.

    Arguments:
        file_name (str): Path to the file.

    Returns:
        bool
    """
    try:
        # pragma pylint: disable=import-error
        from MEDLoader import CheckFileForRead
    except ImportError:
        return get_extension(file_name) in ('med', 'rmed', 'mmed')
    try:
        CheckFileForRead(to_unicode(file_name))
        return True
    except Exception: # pragma pylint: disable=broad-except
        return False

def is_meshfile(file_name):
    """
    Check if a file is a meshfile that has to be converted in med format before
    to be imported as a SMesh object.

    Arguments:
        file_name (str): Path to the file.

    Returns:
        bool
    """
    ext = get_extension(file_name)
    return ext in ('mail', 'mgib', 'msup', 'unv', 'msh') or ext.isdigit()


def get_medfile_meshes(mesh_file):
    """
    Get names of meshes present in MED file.

    Note:
        The function uses MedCoupling library's Python API.

    Arguments:
        mesh_file (str): Path to the MED file.

    Returns:
        list[str]: Names of meshes.

    See also:
        `get_medfile_groups()`, `get_medfile_groups_by_type()`
    """
    meshes = []
    if is_reference(mesh_file):
        mesh_name = external_file(mesh_file)
        if mesh_name is not None:
            meshes.append(mesh_name)
    else:
        try:
            meshes = MESH_CACHE.get_meshes(mesh_file)
            if not meshes:
                # pragma pylint: disable=import-error
                from MEDLoader import GetMeshNames
                meshes = list(GetMeshNames(to_unicode(mesh_file)))
                MESH_CACHE.add_meshes(mesh_file, meshes)
        except Exception: # pragma pylint: disable=broad-except
            pass
    return meshes


@change_cursor
def get_medfile_groups(mesh_file, mesh_name, group_type):
    """
    Get names of groups present in specified mesh of given MED file.

    Note:
        The function uses MedCoupling library's Python API.

    Arguments:
        mesh_file (str): Path to the MED file.
        mesh_name (str): Name of mesh.
        group_type (int): Type of mesh group (see `MeshGroupType`).

    Returns:
        list[str]: Names of mesh groups.

    Raises:
        TypeError: If invalid *group_type* is specified.

    See also:
        `get_medfile_meshes()`, `get_medfile_groups_by_type()`
    """
    if group_type not in (MeshGroupType.GNode, MeshGroupType.GElement):
        raise TypeError("Invalid group type: {}".format(group_type))
    groups = []
    if is_reference(mesh_file):
        # mesh_name is not used for a while
        groups = external_file_groups(mesh_file, group_type)
    else:
        try:
            elem_types = MeshElemType.elem_types(group_type)
            groups = get_medfile_groups_by_type(mesh_file, mesh_name,
                                                elem_types)
        except Exception: # pragma pylint: disable=broad-except
            pass
    return sorted(list(set(groups)))


def get_medfile_groups_by_type(mesh_file, mesh_name, elem_type,
                               with_size=False):
    """
    Get names of groups present in specified mesh of given MED file.

    Note:
        The function uses MedCoupling library's Python API.

    Arguments:
        mesh_file (str): Path to the MED file.
        mesh_name (str): Name of mesh.
        elem_type (int, list[int]): Type(s) of mesh elements
            (see `MeshElemType`).
        with_size (Optional[bool]): Flag specifying that sizes of groups
            should be returned as well. Defaults to *False*.

    Returns:
        list[info]: List of mesh groups' names or tuples where each
        tuple contains name of group and its size - the behavior is
        controlled by *with_size* parameter.

    Raises:
        TypeError: If invalid *elem_type* is specified.

    See also:
        `get_medfile_meshes()`, `get_medfile_groups()`
    """
    elem_types = to_list(elem_type)
    for typ in elem_types:
        if typ not in (MeshElemType.ENode, MeshElemType.E0D,
                       MeshElemType.E1D, MeshElemType.E2D,
                       MeshElemType.E3D):
            raise TypeError("Invalid element type: {}".format(typ))
    groups = []
    if is_reference(mesh_file):
        # mesh_name is not used for a while
        groups = external_file_groups_by_type(mesh_file, elem_types, with_size)
    else:
        try:
            # pragma pylint: disable=import-error
            if not mesh_name:
                meshes = get_medfile_meshes(mesh_file)
                if meshes:
                    mesh_name = meshes[0]
            not_cached = []
            for typ in elem_types:
                if MESH_CACHE.has_groups(mesh_file, mesh_name, typ):
                    cached = MESH_CACHE.get_groups(mesh_file, mesh_name, typ)
                    if with_size:
                        groups += cached
                    else:
                        groups += [i[0] for i in cached]
                else:
                    not_cached.append(typ)
                debug_message("get_medfile_groups_by_type cached", groups, with_size)

            if not_cached:
                from MEDLoader import MEDFileMesh
                med_mesh = MEDFileMesh.New(to_unicode(mesh_file),
                                           to_unicode(mesh_name))
                dim = med_mesh.getMeshDimension()
                for typ in not_cached:
                    if typ == MeshElemType.ENode:
                        mesh_type = 1
                    else:
                        mesh_type = 999 if typ > dim else typ-dim

                    ##adding try/except, due to blindage from getGroupsOnSpecifiedLev
                    ##which automatically failed if the is no group for a type.
                    try :
                        names = list(med_mesh.getGroupsOnSpecifiedLev(mesh_type))
                    except :
                        names = list()

                    new_groups = []
                    for name in names:
                        size = len(med_mesh.getGroupArr(mesh_type, name))
                        occs = max(1, len(med_mesh.getGrpNonEmptyLevels(name)) \
                                    - int(-dim in med_mesh.getGrpNonEmptyLevels(name)))
                        new_groups.append((name, size, occs))
                    MESH_CACHE.add_groups(mesh_file, mesh_name, typ, new_groups)
                    if with_size:
                        groups += new_groups
                    else:
                        groups += [i[0] for i in new_groups]
                debug_message("get_medfile_groups_by_type return", groups, with_size)
        except Exception as exc: # pragma pylint: disable=broad-except
            info_message(exc)
    return groups


@change_cursor
def get_cmd_groups(command, group_type, with_size=False):
    """
    Retrieve names of groups present in specified mesh from Command.

    Arguments:
        command (Command): Command.
        group_type (int): Type of mesh group (see `MeshGroupType`).
        with_size (Optional[bool]): Flag specifying that sizes of groups
            should be returned as well. Defaults to *False*.

    Returns:
        dict[int, info)]: Dictionary where each key is a type of
        mesh element (`MeshElemType`) and value is either a list of
        mesh groups' names or a list of tuples, each tuple contains
        group's name and size - the behavior is controlled by
        *with_size* parameter.

    Raises:
        TypeError: If invalid *group_type* is specified.

    See also:
        `get_medfile_groups_by_type()`
    """
    if group_type not in (MeshGroupType.GNode, MeshGroupType.GElement):
        raise TypeError("Invalid group type: {}".format(group_type))
    groups = {}
    if command is not None:
        storage = command.storage_nocopy
        unite = storage.get('UNITE')
        nom_med = storage.get('NOM_MED')
        maillage = storage.get('MAILLAGE')
        model = storage.get('MODEL')
        if unite is not None:
            stage = command.stage
            file_name = stage.handle2info[unite].filename \
                if unite in stage.handle2info else ''
            if nom_med is None and file_name:
                meshes_med = get_medfile_meshes(file_name)
                if meshes_med:
                    nom_med = meshes_med[0]
            elem_types = MeshElemType.elem_types(group_type)
            for elem_type in elem_types:
                elem_groups = get_medfile_groups_by_type(file_name, nom_med,
                                                         elem_type, with_size)
                groups[elem_type] = elem_groups
        elif maillage is not None:
            groups = get_cmd_groups(maillage, group_type, with_size)
        elif model is not None:
            groups = get_cmd_groups(model, group_type, with_size)
    return groups


def get_cmd_mesh(command):
    """
    Retrieves MED file and name associated with a command

    Note:
        This implementation can only walk up specific dependences,
        those with "MODELE" or "MAILLAGE" keywords.
    """
    file_name = nom_med = None
    if command is not None and hasattr(command, 'storage'):
        stage = command.stage
        if not stage:
            return file_name, nom_med
        storage = command.storage_nocopy
        mformat = storage.get('FORMAT')
        unite = storage.get('UNITE')
        nom_med = storage.get('NOM_MED')
        maillage = storage.get('MAILLAGE')
        model = storage.get('MODELE')
        if unite is not None and mformat in (None, "MED"):
            file_name = stage.handle2info[unite].filename \
                if unite in stage.handle2info else None
            file_name = file_name if \
                is_medfile(file_name) or is_reference(file_name) \
                else None
            if nom_med is None and file_name:
                meshes_med = get_medfile_meshes(file_name)
                if meshes_med:
                    nom_med = meshes_med[0]
        elif maillage is not None:
            file_name, nom_med = get_cmd_mesh(maillage)
        elif model is not None:
            file_name, nom_med = get_cmd_mesh(model)
    if hasattr(command, 'name'):
        debug_message("Command '{0}' is using mesh '{2}' from {1}"
                      .format(command.name, file_name, nom_med))
    return file_name, nom_med


def is_valid_group_name(name):
    """
    Check if given string is a valid mesh group name.

    Arguments:
        name (str): Mesh group name.

    Returns:
        bool: *True* if group name is valid; *False* otherwise.
    """
    return re.match(r"^[a-zA-Z_0-9\-\+\.]{1,24}$", name) is not None \
        if name is not None else False


# The following variables specifies if the caching
# of MED file data is switch ON or OFF
USE_CACHE = True

class CachedMeshData:
    """Cache object for MED file data."""

    def __init__(self):
        """Initialize cache."""
        self._cache = {}

    def get_meshes(self, mesh_file):
        """Get cached names of meshes for given MED file."""
        if not USE_CACHE:
            return []
        return list(self._cache.get(mesh_file, {}).keys())

    def add_mesh(self, mesh_file, mesh_name):
        """Cache mesh name."""
        if not USE_CACHE:
            return
        if mesh_file not in self._cache:
            self._cache[mesh_file] = OrderedDict()
        if mesh_name not in self._cache[mesh_file]:
            self._cache[mesh_file][mesh_name] = OrderedDict()

    def add_meshes(self, mesh_file, meshes):
        """Cache mesh names."""
        if not USE_CACHE:
            return
        for mesh_name in meshes:
            self.add_mesh(mesh_file, mesh_name)

    def has_groups(self, mesh_file, mesh_name, elem_type):
        """Check if there is stored groups data for given mesh."""
        if not USE_CACHE:
            return False
        return mesh_file in self._cache and \
            mesh_name in self._cache[mesh_file] and \
            elem_type in self._cache[mesh_file][mesh_name]

    def get_groups(self, mesh_file, mesh_name, elem_type):
        """
        Get cached groups data of given element type for given mesh.
        """
        groups = {}
        if USE_CACHE:
            meshes = self._cache.get(mesh_file, {})
            elem_types = meshes.get(mesh_name, {})
            groups = elem_types.get(elem_type, {})
        return [tuple([name] + list(info)) for name, info in groups.items()]

    def add_group(self, mesh_file, mesh_name, elem_type, group):
        """Cache group data."""
        if not USE_CACHE:
            return
        if mesh_file not in self._cache:
            self._cache[mesh_file] = OrderedDict()
        if mesh_name not in self._cache[mesh_file]:
            self._cache[mesh_file][mesh_name] = OrderedDict()
        if elem_type not in self._cache[mesh_file][mesh_name]:
            self._cache[mesh_file][mesh_name][elem_type] = OrderedDict()
        if isinstance(group, (list, tuple)):
            assert len(group) == 3
            group_name = group[0]
            group_info = group[1:3] # size and nb occurrences
        else:
            group_name = group
            group_info = [0, 1]
        if group_name not in self._cache[mesh_file][mesh_name][elem_type]:
            self._cache[mesh_file][mesh_name][elem_type][group_name] = \
                group_info

    def add_groups(self, mesh_file, mesh_name, elem_type, groups):
        """Cache groups data."""
        if not USE_CACHE:
            return
        for group in groups:
            self.add_group(mesh_file, mesh_name, elem_type, group)

    def clear_cache(self, mesh_file=None, mesh_name=None, elem_type=None):
        """Clear cache."""
        if mesh_file is None:
            self._cache.clear()
        elif mesh_name is None:
            if mesh_file in self._cache:
                del self._cache[mesh_file]
        elif elem_type is None:
            if mesh_file in self._cache and \
                    mesh_name in self._cache[mesh_file]:
                del self._cache[mesh_file][mesh_name]
        else:
            if mesh_file in self._cache and \
                    mesh_name in self._cache[mesh_file] and \
                    elem_type in self._cache[mesh_file][mesh_name]:
                del self._cache[mesh_file][mesh_name][elem_type]

# MED file data cache object (singleton)
MESH_CACHE = CachedMeshData()
