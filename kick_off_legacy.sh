#!/bin/bash
HERE="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

if pgrep roll_one.py &> /dev/null ; then
    echo "rollone running." &> /dev/null
    echo "rollone really good like." &> /dev/null
else
    echo "Kicking off run_legacy.py..."
    ( ${HERE}/run_legacy.py --long-lived 2>&1 >> ${HERE}/rofm.log & )
fi
