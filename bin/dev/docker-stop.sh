#!/bin/bash
: "${PROJECT_NAME:=template-whatsapp}"

CONTAINER_NAME="${PROJECT_NAME}"

if  docker ps -a | grep "$CONTAINER_NAME$"; then
    docker stop $CONTAINER_NAME
    docker rm $CONTAINER_NAME
else
    echo "Container not running."
fi
