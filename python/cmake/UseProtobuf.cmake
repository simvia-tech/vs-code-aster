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

#
# Implements auxiliary macros for build procedure:
# - PROTOBUF_GENERATE_PY : parse proto file(s) and generate Python
#                          source file.
#

###
# Macro: PROTOBUF_GENERATE_PY
# Description: Generate Python source file from proto file(s).
#
# Usage: PROTOBUF_GENERATE_CPP(outfiles outdir infile ...)
#        outfiles - variable to list output files (Python modules)
#        outdir - directory path for output files
#        infile - one or more input proto files
#
function(PROTOBUF_GENERATE_PY outfiles outdir)
  set(_infiles)
  set(_opts)
  foreach(_input ${ARGN})
    get_filename_component(_input_we ${_input} NAME_WE)
    get_filename_component(_abs_input ${_input} ABSOLUTE)
    get_filename_component(_abs_dir ${_abs_input} PATH)
    list(APPEND _infiles ${_abs_input})
    list(APPEND ${outfiles} ${outdir}/${_input_we}_pb2.py)
    list(APPEND _opts -I${_abs_dir})
  endforeach()
  if(_infiles)
    file(RELATIVE_PATH _target_name ${CMAKE_SOURCE_DIR} ${CMAKE_CURRENT_SOURCE_DIR})
    string(REGEX REPLACE "/|\\.|:" "_" _target_name "${_target_name}")
    set(_target_name "${_target_name}_protobuf_py")
    add_custom_command(OUTPUT ${${outfiles}}
      COMMAND ${PROTOBUF_PROTOC_EXECUTABLE}
      ARGS ${_opts} --python_out=${outdir} ${_infiles}
      DEPENDS ${_infiles} VERBATIM)
    set(${outfiles} ${${outfiles}} PARENT_SCOPE)
  endif()
endfunction()
