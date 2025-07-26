#!/bin/bash

python3 -m venv .venv
source .venv/bin/activate
pip3 install -r requirements.txt
uvicorn main:app --port 5000 --reload --log-level debug