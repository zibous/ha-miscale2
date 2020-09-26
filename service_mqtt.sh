#!/bin/sh
set -e
SCRIPT_DIR=$( cd "$( dirname "$0" )" >/dev/null 2>&1 && pwd )

cd "$SCRIPT_DIR"
python3 ./mqttservice.py "$@"