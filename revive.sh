#!/bin/bash
if pgrep roll_one.py &> /dev/null ; then
    echo "rollone running." &> /dev/null
    echo "rollone really good like." &> /dev/null
else
    echo "rollone offline.  Restoring..."
    # double-fork might escape problem of child process not properly spawning.
    ( /home/pi/robots/roll_one_for_me/roll_one.py any_input_to_run & )
    sleep 30
    if pgrep roll_one.py &> /dev/null ; then
        echo "Successfully restored."
    else
        echo "Restoration failed."
    fi
fi
