#!/bin/bash
source venv/bin/activate
export FLASK_APP=app.py
export FLASK_DEBUG=True
nohup flask run -h 0.0.0.0 -p 10000 &
