#!/bin/bash
PYTHONPATH=${PWD}/src poetry run streamlit run `echo "${@:1}"` \
    # the echo part file name taken from the command line as input
    # port for streamlit
    --server.port 8502 \
    # extra
    --server.enableXsrfProtection false \
    --server.enableCORS false

