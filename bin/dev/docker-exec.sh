#!/bin/bash
: "${PROJECT_NAME:=template-whatsapp}"

docker exec -i -t $PROJECT_NAME `echo "${@:1}"`