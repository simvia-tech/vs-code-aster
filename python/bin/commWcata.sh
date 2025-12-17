#!/bin/bash

########################################################################
# Wrapper over the `commWcata` executable.
########################################################################

commWcata_main()
{
    local where=$(readlink -f $(dirname "${0}"))

    ASTERSTUDY_SILENT_MODE=1 # avoid possible printouts from env.sh
    test "${ASTERSTUDYDIR}x" = "x" && test -e ${where}/../dev/env.sh && . ${where}/../dev/env.sh

    python3 "$where/commWcata" "$@"
}

commWcata_main "$@"
exit $?
