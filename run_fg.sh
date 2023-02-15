#!/bin/bash
set -euo pipefail

cd "$(dirname "$0")"
source venv/bin/activate
export FLASK_APP=app.py
# export FLASK_ENV=development
export FLASK_DEBUG=True
flask run -h 0.0.0.0 -p 10000
deactivate
