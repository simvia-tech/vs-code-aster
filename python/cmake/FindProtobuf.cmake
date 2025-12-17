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

# Find Protobuf installation
#
# Note: This procedure is different from what is done by FindProtobuf
# detection utility included into the CMake. In fact, we need only
# protoc executable and don't need other staff (headers, libs).
# So, this is a "light" version of Protobuf detection procedure.
#
# Sets the following variables:
#     PROTOBUF_PROTOC_EXECUTABLE - path to the protoc executable
#     PROTOBUF_VERSION           - version of Protobuf
#     PROTOBUF_FOUND             - TRUE if Protobuf has been found.

find_program(PROTOBUF_PROTOC_EXECUTABLE NAMES protoc)

get_filename_component(PROTOBUF_DIR "${PROTOBUF_PROTOC_EXECUTABLE}" PATH)
get_filename_component(PROTOBUF_DIR "${PROTOBUF_DIR}" PATH)

if(PROTOBUF_PROTOC_EXECUTABLE)
  execute_process(COMMAND ${PROTOBUF_PROTOC_EXECUTABLE} "--version" OUTPUT_VARIABLE PROTOBUF_VERSION OUTPUT_STRIP_TRAILING_WHITESPACE)
  string(REGEX REPLACE ".* ([0-9.]+)$" "\\1" PROTOBUF_VERSION "${PROTOBUF_VERSION}")
endif()

include(FindPackageHandleStandardArgs)
find_package_handle_standard_args(Protobuf REQUIRED_VARS PROTOBUF_PROTOC_EXECUTABLE)
