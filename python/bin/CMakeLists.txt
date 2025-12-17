# Copyright 2016-2019 EDF R&D
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

# Install executables
set(_BIN_PYFILES
  ajs2apb 
  ajs2ast
  apb2ajs
  apb2ast
  ast2ajs
  ast2apb
  asterstudy_assistant
  asterstudy
  comm2code
  comm2study
  debug_ajs
  commWcata
)
set(_BIN_SCRIPTS
  asterstudy.sh
  asterstudy_assistant.sh
  comm2code.sh
  comm2study.sh
  commWcata.sh
)

foreach(_bin_pyfile ${_BIN_PYFILES})
  configure_file(${_bin_pyfile} ${CMAKE_CURRENT_BINARY_DIR}${CMAKE_FILES_DIRECTORY}/${_bin_pyfile} @ONLY)
  install(FILES ${CMAKE_CURRENT_BINARY_DIR}${CMAKE_FILES_DIRECTORY}/${_bin_pyfile}
          DESTINATION ${ASTERSTUDY_BIN_DIR}
          PERMISSIONS OWNER_READ OWNER_WRITE OWNER_EXECUTE GROUP_READ GROUP_EXECUTE WORLD_READ WORLD_EXECUTE)
endforeach()

install(FILES ${_BIN_SCRIPTS}
        DESTINATION ${ASTERSTUDY_BIN_DIR}
        PERMISSIONS OWNER_READ OWNER_WRITE OWNER_EXECUTE GROUP_READ GROUP_EXECUTE WORLD_READ WORLD_EXECUTE)
