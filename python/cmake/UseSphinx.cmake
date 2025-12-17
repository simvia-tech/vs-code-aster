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
# - INSTALL_SPHINX_DOCS : build and install documentation with Sphinx
#

###
# Macro: INSTALL_SPHINX_DOCS
# Description: Build documentation with Sphinx and install it to the 
#              destination folder.
#
# Usage: INSTALL_SPHINX_DOCS(DESTINATION destdir [SRCDIR srcdir] [CFGDIR cfgdir]
#                            [BUILDDIR builddir] [LANGUAGES langs] [OPTIONS options])
#        destdir   - destination directory.
#        srcdir    - source directory (optional); by default current source dir is used.
#        cfgdir    - config.py location (optional); by default source directory is used.
#        builddir  - build directory (optional); by default current build dir is used.
#        langs     - extra languages (optional), if multi-language support is enabled.
#        options   - Sphinx options (optional).
#
macro(INSTALL_SPHINX_DOCS)
  cmake_parse_arguments(_INSTALL_SPHINX_DOCS "" "DESTINATION;SRCDIR;CFGDIR;BUILDDIR;LANGUAGES" "OPTIONS" ${ARGN})

  if(NOT _INSTALL_SPHINX_DOCS_DESTINATION)
    message(FATAL_ERROR "Destination folder is not specified!")
  endif()

  set(_install_dir ${_INSTALL_SPHINX_DOCS_DESTINATION})

  set(_src_dir ${_INSTALL_SPHINX_DOCS_SRCDIR})
  if("${_src_dir}" STREQUAL "")
    set(_src_dir ${CMAKE_CURRENT_SOURCE_DIR})
  endif()

  set(_cfg_dir ${_INSTALL_SPHINX_DOCS_CFGDIR})
  if("${_cfg_dir}" STREQUAL "")
    set(_cfg_dir ${_src_dir})
  endif()

  set(_build_dir ${_INSTALL_SPHINX_DOCS_BUILDDIR})
  if("${_build_dir}" STREQUAL "")
    set(_build_dir _build)
  endif()
  if(NOT IS_ABSOLUTE ${_build_dir})
    set(_build_dir ${CMAKE_CURRENT_BINARY_DIR}/${_build_dir})
  endif()

  file(RELATIVE_PATH _target_name ${CMAKE_SOURCE_DIR} ${CMAKE_CURRENT_SOURCE_DIR})
  string(REGEX REPLACE "/|\\.|:" "_" _target_name "${_target_name}")
  set(_target_name "${_target_name}_html")

  add_custom_target(${_target_name}
                    env PYTHONPATH=${CMAKE_SOURCE_DIR}:$ENV{PYTHONPATH}
                    ${SPHINX_BUILD_EXECUTABLE}
                    -b html -c ${_cfg_dir} -d ${_build_dir}/doctrees}
                    ${_INSTALL_SPHINX_DOCS_OPTIONS}
                    ${_src_dir} ${_build_dir}/html)

  install(CODE "execute_process(COMMAND \"${CMAKE_COMMAND}\" --build ${PROJECT_BINARY_DIR} --target ${_target_name})")
  install(DIRECTORY ${_build_dir}/html DESTINATION ${_install_dir} USE_SOURCE_PERMISSIONS  PATTERN ".buildinfo" EXCLUDE)
  
  if(SPHINX_MULTILANG_SUPPORT AND _INSTALL_SPHINX_DOCS_LANGUAGES)
    add_custom_target(${_target_name}_pot
                      env PYTHONPATH=${CMAKE_SOURCE_DIR}:$ENV{PYTHONPATH}
                      ${SPHINX_BUILD_EXECUTABLE}
                      -b gettext -c ${_cfg_dir}
                      ${_INSTALL_SPHINX_DOCS_OPTIONS}
                      ${_src_dir} ${_build_dir}/potfiles)

    set(_languages)
    foreach(_language ${_INSTALL_SPHINX_DOCS_LANGUAGES})
      list(APPEND _languages -l)
      list(APPEND _languages ${_language})
    endforeach()
    add_custom_target(${_target_name}_update
                      env PYTHONPATH=${CMAKE_SOURCE_DIR}:$ENV{PYTHONPATH}
                      ${SPHINX_INTL_EXECUTABLE} update
                      -p ${_build_dir}/potfiles -d ${_src_dir}/locale ${_languages})

    add_custom_target(${_target_name}_mo
                      env PYTHONPATH=${CMAKE_SOURCE_DIR}:$ENV{PYTHONPATH}
                      ${SPHINX_INTL_EXECUTABLE} build
                      -d ${_src_dir}/locale -o ${_build_dir}/locale)

    SET(CMDS "${CMDS} ${SPHINX_INTL_EXECUTABLE} build\n")

    add_dependencies(${_target_name} ${_target_name}_mo)
    add_dependencies(${_target_name}_mo ${_target_name}_update)
    add_dependencies(${_target_name}_update ${_target_name}_pot)

    foreach(_language ${_INSTALL_SPHINX_DOCS_LANGUAGES})
      add_custom_target(${_target_name}_${_language}
                        env PYTHONPATH=${CMAKE_SOURCE_DIR}:$ENV{PYTHONPATH}
                        ${SPHINX_BUILD_EXECUTABLE}
                        -b html -c ${_cfg_dir} -d ${_build_dir}/doctrees}
                        -D language=${_language}
                        ${_INSTALL_SPHINX_DOCS_OPTIONS}
                        ${_src_dir} ${_build_dir}/html_${_language})

      add_dependencies(${_target_name} ${_target_name}_${_language})
      add_dependencies(${_target_name}_${_language} ${_target_name}_mo)
      install(DIRECTORY ${_build_dir}/html_${_language} DESTINATION ${_install_dir} USE_SOURCE_PERMISSIONS  PATTERN ".buildinfo" EXCLUDE)

    endforeach()

  endif()

  set_directory_properties(PROPERTIES ADDITIONAL_MAKE_CLEAN_FILES ${_build_dir})
endmacro()
