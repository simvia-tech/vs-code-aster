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

# Find Coverage installation
# Sets the following variables:
#     COVERAGE_DIR              - path to the Coverage root directory
#     COVERAGE_VERSION          - version of Coverage
#     COVERAGE_EXECUTABLE       - path to the coverage executable
#     COVERAGE_FOUND            - TRUE if Coverage has been found.

find_program(COVERAGE_EXECUTABLE NAMES coverage)

get_filename_component(COVERAGE_DIR "${COVERAGE_EXECUTABLE}" PATH)
get_filename_component(COVERAGE_DIR "${COVERAGE_DIR}" PATH)

if(COVERAGE_EXECUTABLE)
  execute_process(COMMAND ${COVERAGE_EXECUTABLE} "--version" OUTPUT_VARIABLE COVERAGE_VERSION OUTPUT_STRIP_TRAILING_WHITESPACE)
  string(REGEX REPLACE ".* ([0-9.]+).*" "\\1" COVERAGE_VERSION "${COVERAGE_VERSION}")
endif()

include(FindPackageHandleStandardArgs)
find_package_handle_standard_args(Coverage REQUIRED_VARS COVERAGE_EXECUTABLE)
