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
# Implements auxiliary utilities for build procedure:
# - INSTALL_PYTHON_SCRIPTS : install Python module(s)
# - INSTALL_PYTHON_DIRS    : install Python package(s)
# - ADD_PYTHON_TESTS       : add tests
#

###
# Macro: INSTALL_PYTHON_SCRIPTS
# Description: Install Python modules and optionally generate byte-code files.
#
# Usage: INSTALL_PYTHON_SCRIPTS(scripts DESTINATION destdir)
#        scripts - Python module(s) to install
#        destdir - destination directory
#
# Byte-code files (both regular and optimized versions) are automatically
# generated and installed along with Python modules if COMPILE_PYFILES variable
# is set to ON.
#
macro(INSTALL_PYTHON_SCRIPTS)
  cmake_parse_arguments(_INSTALL_PYTHON_SCRIPTS "" "DESTINATION" "" ${ARGN})
  set(_pyfiles ${_INSTALL_PYTHON_SCRIPTS_UNPARSED_ARGUMENTS})
  set(_install_dir ${_INSTALL_PYTHON_SCRIPTS_DESTINATION})
  foreach(_file ${_pyfiles})
    if(NOT IS_ABSOLUTE ${_file})
      set(_src_file ${CMAKE_CURRENT_SOURCE_DIR}/${_file})
    else()
      set(_src_file ${_file})
    endif()
    if(NOT EXISTS ${_src_file})
      message(FATAL_ERROR "No such file: ${_src_file}!")
    endif()
    get_filename_component(_file_name ${_file} NAME)
    get_filename_component(_file_name_we ${_file_name} NAME_WE)
    install(FILES ${_file} DESTINATION ${CMAKE_INSTALL_PREFIX}/${_install_dir})
    if(COMPILE_PYFILES)
      # TODO: implement compile pyfiles feature
    endif(COMPILE_PYFILES)
  endforeach()
  if(COMPILE_PYFILES) # TODO: to be removed as soon as this feature is implemented
    install(CODE "message(WARNING \"COMPILE_PYFILES feature is not supported yet!\")")
  endif(COMPILE_PYFILES)
endmacro()

###
# Macro: INSTALL_PYTHON_DIRS
# Description: Install Python packages and optionally generate byte-code files,
# The sub-tree of each source directory is kept in the destination folder.
#
# Usage: INSTALL_PYTHON_DIRS(dirs DESTINATION destdir [EXCLUDE pattern [pattern ...]])
#        dirs    - Python package(s) to install
#        destdir - destination directory
#        pattern - pattern for modules to be excluded from installation
#
# Byte-code files (both regular and optimized versions) are automatically
# generated and installed along with Python modules if COMPILE_PYFILES variable
# is set to ON.
#
macro(INSTALL_PYTHON_DIRS)
  cmake_parse_arguments(_INSTALL_PYTHON_DIRS "" "DESTINATION" "EXCLUDE" ${ARGN})
  set(_dirs ${_INSTALL_PYTHON_DIRS_UNPARSED_ARGUMENTS})
  set(_install_dir ${_INSTALL_PYTHON_DIRS_DESTINATION})
  set(_excludes ${_INSTALL_PYTHON_DIRS_EXCLUDE})
  list(APPEND _excludes ".#*")
  set(_exclude_all "")
  foreach(_exclude ${_excludes})
    string(REPLACE "." "[.]" _exclude_out "${_exclude}")
    string(REPLACE "*" ".*" _exclude_out "${_exclude_out}")
    string(REPLACE "?" "." _exclude_out "${_exclude_out}")
    if("${_exclude_all}" STREQUAL "")
      set(_exclude_all "${_exclude_out}")
    else()
      set(_exclude_all "${_exclude_all}|${_exclude_out}")
    endif()
  endforeach()
  set(_exclude_all "^(${_exclude_all})$")
  foreach(_dir ${_dirs})
    if(NOT EXISTS ${CMAKE_CURRENT_SOURCE_DIR}/${_dir})
      message(FATAL_ERROR "No such directory: ${CMAKE_CURRENT_SOURCE_DIR}/${_dir}!")
    endif()
    get_filename_component(_dirname ${_dir} NAME)
    file(GLOB_RECURSE _pyfiles "${_dir}/*.py")
    foreach(_file ${_pyfiles})
      file(RELATIVE_PATH _file_name ${CMAKE_CURRENT_SOURCE_DIR}/${_dir} ${_file})
      get_filename_component(_file_name_we ${_file_name} NAME_WE)
      get_filename_component(_file_name_wi ${_file_name} NAME)
      if(NOT "${_file_name_wi}" MATCHES "${_exclude_all}")
        get_filename_component(_file_dir ${CMAKE_INSTALL_PREFIX}/${_install_dir}/${_dirname}/${_file_name} PATH)
      	install(FILES ${_file} DESTINATION ${_file_dir})
        if(COMPILE_PYFILES)
          # TODO: implement compile pyfiles feature
        endif(COMPILE_PYFILES)
      endif()
    endforeach()
  endforeach()
  if(COMPILE_PYFILES) # TODO: to be removed as soon as this feature is implemented
    install(CODE "message(WARNING \"COMPILE_PYFILES feature is not supported yet!\")")
  endif(COMPILE_PYFILES)
endmacro()

###
# Macro: ADD_PYTHON_TESTS
# Description: Add tests running with Python executable.
#
# Usage: ADD_PYTHON_TESTS(scripts)
#        scripts - Python script(s) to be added as tests
#
macro(ADD_PYTHON_TESTS)
  foreach(_test ${ARGN})
    file(RELATIVE_PATH _test_path ${CMAKE_SOURCE_DIR} ${CMAKE_CURRENT_SOURCE_DIR}/${_test})
    string(REGEX REPLACE "/|\\.|:" "_" _test_name "${_test_path}")
    if(NOSE_FOUND)
      add_test(NAME ${_test_name} WORKING_DIRECTORY ${CMAKE_INSTALL_PREFIX} COMMAND ${NOSE_NOSETESTS_EXECUTABLE} -c ${CMAKE_SOURCE_DIR}/test/.noserc ${CMAKE_CURRENT_SOURCE_DIR}/${_test})
    else()
      add_test(NAME ${_test_name} WORKING_DIRECTORY ${CMAKE_INSTALL_PREFIX} COMMAND ${PYTHON_EXECUTABLE} -B ${CMAKE_CURRENT_SOURCE_DIR}/${_test})
    endif()
    set_tests_properties(${_test_name} PROPERTIES ENVIRONMENT "PYTHONPATH=${CMAKE_INSTALL_PREFIX}/lib/python${PYTHON_VERSION_MAJOR}.${PYTHON_VERSION_MINOR}/site-packages:${CMAKE_SOURCE_DIR}/test:$ENV{PYTHONPATH};ASTERSTUDY_WITHIN_TESTS=1")
  endforeach()
endmacro()
