#!/bin/bash

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

########################################################################
# Wrapper over the `comm2code` executable.
########################################################################

comm2code_main()
{
    local where=$(readlink -f $(dirname "${0}"))

    ASTERSTUDY_SILENT_MODE=1 # avoid possible printouts from env.sh
    test "${ASTERSTUDYDIR}x" = "x" && test -e ${where}/../dev/env.sh && . ${where}/../dev/env.sh

    comm2code "${@}"
}

comm2code_main "${@}"
exit ${?}
