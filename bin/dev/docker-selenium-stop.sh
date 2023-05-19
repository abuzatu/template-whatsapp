#!/bin/bash
: "${PROJECT_NAME:=standalone-selenium-chrome}"

CONTAINER_NAME="${PROJECT_NAME}"

if  docker ps -a | grep "$CONTAINER_NAME$"; then
    docker stop $CONTAINER_NAME
    # stop will also remove it, so no need to have a line to remove
else
    echo "Container not running."
fi