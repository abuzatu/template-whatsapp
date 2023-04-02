#!/bin/bash
: "${PROJECT_NAME:=template-whatsapp}"

docker exec -i -t  ${PROJECT_NAME} \
    poetry run dotenv run ipython