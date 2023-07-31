#!/bin/bash
# set -euo pipefail
export FLASK_APP=/app/app.py
export FLASK_DEBUG=True
flask run -h 0.0.0.0 -p 10000