#!/bin/bash

if [ $(whoami) != root ]; then
    echo "You must be root in order to use the backup script"
fi

local_dir="$(dirname "$0")"
if [ -n "$PYTHONPATH" ]; then
    export PYTHONPATH="$PYTHONPATH:$local_dir/src"
else
    export PYTHONPATH="$local_dir/src"
fi

python -m main "$@"
