#!/bin/bash
: "${PROJECT_NAME:=standalone-chromium}"

docker exec -i -t  $PROJECT_NAME /bin/bash