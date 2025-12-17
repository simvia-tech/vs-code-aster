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

# Find PyQt5 installation
# Sets the following variables:
#     PyQt5_DIR               - path to the PyQt5 root directory
#     PyQt5_PYUIC_EXECUTABLE  - path to the pyuic5 executable
#     PyQt5_PYRCC_EXECUTABLE  - path to the pyrcc5 executable
#     PYQT5_FOUND             - TRUE if all components are found.

if(NOT PYTHONINTERP_FOUND)
  message(FATAL_ERROR "The PyQt5 package requires Python to be detected first")
endif()

if(NOT PyQt5_FIND_COMPONENTS)
  message(FATAL_ERROR "The PyQt5 package requires at least one component")
endif()

foreach(module ${PyQt5_FIND_COMPONENTS})
  execute_process(COMMAND ${PYTHON_EXECUTABLE} -c "from PyQt5 import Qt${module}; print(Qt${module})"
                  RESULT_VARIABLE _ok OUTPUT_QUIET ERROR_QUIET)
  if(_ok)
    message(FATAL_ERROR "The PyQt5 module ${module} is not found: ${_out}")
  endif()
endforeach()

find_program(PyQt5_PYUIC_EXECUTABLE NAMES pyuic5 pyuic5.bat)
find_program(PyQt5_PYRCC_EXECUTABLE NAMES pyrcc5 pyrcc5.bat)

get_filename_component(PyQt5_DIR "${PyQt5_PYUIC_EXECUTABLE}" PATH)
get_filename_component(PyQt5_DIR "${PyQt5_DIR}" PATH)

include(FindPackageHandleStandardArgs)
find_package_handle_standard_args(PyQt5 REQUIRED_VARS PyQt5_DIR PyQt5_PYUIC_EXECUTABLE PyQt5_PYRCC_EXECUTABLE)
