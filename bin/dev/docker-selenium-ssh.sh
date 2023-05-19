#!/bin/bash
: "${PROJECT_NAME:=standalone-selenium-chrome}"

docker exec -i -t  $PROJECT_NAME /bin/bash