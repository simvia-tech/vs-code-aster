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
# - QT_CREATE_TRANSLATION : generate translation file(s) from Python modules
#

###
# Function: QT_CREATE_TRANSLATION
# Description: Parse Python code and generate translation file(s)
#
# It is a wrapper around standard QT5_CREATE_TRANSLATION function provided
# within Qt5LinguistTools Qt CMake module.
# Qt lupdate tool is able to extract translations from Python modules, but
# in some cases it fails to detect translations, so this wrapper allows to
# cope with these problems. See pylupdate for more details.
#
# Usage: QT_CREATE_TRANSLATION(outfiles infile ... [GENERATED dummyfile])
#        outfiles - variable to list output files (Qt compiled translations)
#        infile - input file; TS file or input Python module/package
#        dummyfile - optional dummy output file to put extracted translations
#
# Number of *.qm output files corresponds to the number of input *.ts files;
# remaining input files are considered as source code to be parsed.
#
# Note: The function extracts all translatable strings from the source code
# and puts it into the dummy output file which is then passed to Qt lupdate
# tool. Default name of dummy file is hardcoded, so several invokations of 
# QT_CREATE_TRANSLATION in the same CMakeLists.txt will conflict to each other.
# This problem can be avoided by specifying custom name via the optional
# GENERATED option.
#
function(QT_CREATE_TRANSLATION _qm_files)
  cmake_parse_arguments(_QT_CREATE_TRANSLATION "" "GENERATED" "" ${ARGN})
  if(_QT_CREATE_TRANSLATION_GENERATED)
    set(_generated_file "${CMAKE_CURRENT_BINARY_DIR}${CMAKE_FILES_DIRECTORY}/${_QT_CREATE_TRANSLATION_GENERATED}")
  else()
    set(_generated_file "${CMAKE_CURRENT_BINARY_DIR}${CMAKE_FILES_DIRECTORY}/dummy_generated.py")
  endif()
  set(_ts_files)
  set(_sources)

  foreach(_file ${_QT_CREATE_TRANSLATION_UNPARSED_ARGUMENTS})
    get_filename_component(_ext ${_file} EXT)
    get_filename_component(_abs_file ${_file} ABSOLUTE)
    if(_ext MATCHES "ts")
      list(APPEND _ts_files ${_abs_file})
    else()
      list(APPEND _sources ${_abs_file})
    endif()
  endforeach()

  # We use a workaround here in order to update ts file(s) always,
  # to solve problem with dependencies which may happen with Mercurial
  # that sometimes does not set modification time correctly when switching
  # between revisions. See https://www.mercurial-scm.org/wiki/FAQ/CommonProblems.
  # To solve this, we declare additional output file always_rebuild which in fact
  # is not generated.

  add_custom_command(OUTPUT ${_generated_file} always_rebuild
                     COMMAND ${CMAKE_SOURCE_DIR}/cmake/pylupdate
                     ARGS -e py,res -s -o ${_generated_file} ${_sources}
                     DEPENDS ${_sources}
                     VERBATIM)

  qt5_create_translation(${_qm_files} ${_ts_files} ${_generated_file} OPTIONS -extensions py -locations none -no-obsolete)

  set(${_qm_files} ${${_qm_files}} PARENT_SCOPE)
endfunction()
