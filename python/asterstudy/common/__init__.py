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

"""Common purpose utilities and services."""


from .base_utils import (Singleton, add_extension, copy_file, current_time,
                         get_absolute_dirname, get_absolute_path,
                         get_base_name, get_extension, is_localhost,
                         is_subpath, is_valid_file_path, localhost_server,
                         make_dirs, move_file, no_new_attributes, ping,
                         read_file, remove_path, rotate_path, same_path,
                         split_text, str2tuple, tail_file, to_unicode,
                         valid_file_name, write_file)
from .excepthook import enable_except_hook
from .exceptions import (AsterStudyError, AsterStudyInterrupt, CatalogError,
                         ConversionError, CyclicDependencyError,
                         ExistingSwapError, MissingStudyDirError, RunnerError,
                         StudyDirectoryError, VersionError,
                         WritingToExistingFileError)
from .extfiles import (FilesSupplier, MeshElemType, MeshGroupType,
                       external_file, external_files, external_files_callback,
                       get_cmd_groups, get_cmd_mesh, get_medfile_groups,
                       get_medfile_groups_by_type, get_medfile_meshes,
                       is_medfile, is_meshfile, is_reference,
                       is_valid_group_name)
from .features import Features
from .session import AsterStudySession
from .version import version
