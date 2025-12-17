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

# Find Sphinx installation
# Sets the following variables:
#     SPHINX_DIR                - path to the Sphinx root directory
#     SPHINX_VERSION            - version of Sphinx
#     SPHINX_BUILD_EXECUTABLE   - path to the sphinx-build executable
#     SPHINX_APIDOC_EXECUTABLE  - path to the sphinx-apidoc executable
#     SPHINX_AUTOGEN_EXECUTABLE - path to the sphinx-autogen executable
#     SPHINX_INTL_EXECUTABLE    - path to the sphinx-intl executable (optional)
#     SPHINX_MULTILANG_SUPPORT  - TRUE if multi-language support is enabled
#     SPHINX_FOUND              - TRUE if all components are found.
# Additional features:
#     Sphinx_EXTENSIONS optional variable can be used to specify a list of
#     required Sphinx extensions. By default this variable is empty.
#     Missing extensions are reported during the detection procedure.
#     For each extension, the CMake variable SPHINX_EXT_<name>_FOUND is set,
#     where <name> is a capitalized extension's name with all dots replaced
#     by underscores.
#     Example:
#         set(Sphinx_EXTENSIONS sphinxcontrib.napoleon)
#     checks availability of napoleon extension for Sphinx and sets
#     SPHINX_EXT_SPHINXCONTRIB_NAPOLEON_FOUND variable correspondingly.

if(NOT PYTHONINTERP_FOUND)
  message(FATAL_ERROR "The Sphinx package requires Python to be detected first")
endif()

find_program(SPHINX_BUILD_EXECUTABLE
             NAMES sphinx-build sphinx-build-${PYTHON_VERSION_MAJOR}.${PYTHON_VERSION_MINOR}
             PATH_SUFFIXES Scripts)
find_program(SPHINX_APIDOC_EXECUTABLE
             NAMES sphinx-apidoc sphinx-apidoc-${PYTHON_VERSION_MAJOR}.${PYTHON_VERSION_MINOR}
             PATH_SUFFIXES Scripts)
find_program(SPHINX_AUTOGEN_EXECUTABLE
             NAMES sphinx-autogen sphinx-autogen-${PYTHON_VERSION_MAJOR}.${PYTHON_VERSION_MINOR}
             PATH_SUFFIXES Scripts)
find_program(SPHINX_INTL_EXECUTABLE
             NAMES sphinx-intl sphinx-intl-${PYTHON_VERSION_MAJOR}.${PYTHON_VERSION_MINOR}
             PATH_SUFFIXES Scripts)

get_filename_component(SPHINX_DIR "${SPHINX_BUILD_EXECUTABLE}" PATH)
get_filename_component(SPHINX_DIR "${SPHINX_DIR}" PATH)

if(SPHINX_BUILD_EXECUTABLE)
  execute_process(COMMAND ${SPHINX_BUILD_EXECUTABLE} "--version"
                  OUTPUT_VARIABLE SPHINX_VERSION
                  ERROR_VARIABLE SPHINX_VERSION_FALLBACK
                  OUTPUT_STRIP_TRAILING_WHITESPACE
                  ERROR_STRIP_TRAILING_WHITESPACE)
  if(NOT SPHINX_VERSION)
    set(SPHINX_VERSION "${SPHINX_VERSION_FALLBACK}")
  endif()
  string(REGEX REPLACE ".* ([0-9.]+)$" "\\1" SPHINX_VERSION "${SPHINX_VERSION}")
endif()

include(FindPackageHandleStandardArgs)
find_package_handle_standard_args(Sphinx REQUIRED_VARS SPHINX_BUILD_EXECUTABLE SPHINX_APIDOC_EXECUTABLE SPHINX_AUTOGEN_EXECUTABLE)

if (SPHINX_INTL_EXECUTABLE)
  set(SPHINX_MULTILANG_SUPPORT TRUE)
  message(STATUS "-- Multi-language support is enabled")
else()
  set(SPHINX_MULTILANG_SUPPORT FALSE)
  message(WARNING "-- Multi-language support is DISABLED")
endif()

foreach(_ext ${Sphinx_EXTENSIONS})
  string(TOUPPER ${_ext} _ext_found)
  string(REGEX REPLACE "\\." "_" _ext_found "${_ext_found}")
  set(_ext_found "SPHINX_EXT_${_ext_found}_FOUND")
  execute_process(COMMAND ${PYTHON_EXECUTABLE} -c "import ${_ext}; print('ok')"
                  OUTPUT_VARIABLE _has_ext
                  ERROR_QUIET)
  if(_has_ext)
    set(${_ext_found} TRUE)
    message(STATUS "-- Required Sphinx extension '${_ext}' has been found")
  else()
    set(${_ext_found} FALSE)
    message(WARNING "Required Sphinx extension '${_ext}' is not found!")
  endif()
endforeach()
