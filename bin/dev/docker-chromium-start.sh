#!/bin/bash
: "${PROJECT_NAME:=standalone-chromium}"

CONTAINER_NAME="${PROJECT_NAME}"


if  docker ps | grep " $PROJECT_NAME$"; then
    echo "Container already started. Do nothing"
elif docker ps -a | grep " $PROJECT_NAME$" ; then
    docker start $PROJECT_NAME
else
    # create a container from the image, if image not present it gets downloaded first
    docker run --rm -it -d -p 4444:4444 -p 5900:5900 -p 7900:7900 \
	--name ${CONTAINER_NAME} --shm-size 2g seleniarm/standalone-chromium:latest
    # create the Whatsapp profile folder to avoid scanning Whatsapp every time
    docker exec -i -t ${CONTAINER_NAME} \
	mkdir -p /home/seluser/.config/chromium/google-chrome/Whatsapp
fi