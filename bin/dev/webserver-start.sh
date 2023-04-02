#!/bin/bash
API_KEY=foo PYTHONPATH=${PWD}/src poetry run uvicorn api:app --reload --port 8012 --host 0.0.0.0
