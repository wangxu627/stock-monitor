#!/bin/bash
set -euo pipefail

cd "$(dirname "$0")"
source venv/bin/activate
export FLASK_APP=app.py
export FLASK_DEBUG=True
nohup flask run -h 0.0.0.0 -p 4009 > output.log 2>&1 & echo $! > pid.txt
deactivate

