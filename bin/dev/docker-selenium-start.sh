#!/bin/bash
: "${PROJECT_NAME:=standalone-selenium-chrome}"

CONTAINER_NAME="${PROJECT_NAME}"

# find on what machine we are, local or on server
if [ "$(uname -m)" = "arm64" ]; then
    echo "We are local on MacOS M1"
    # Chrome does not offer binaries for M1, so we need to use
    # another image, built by communty seleriarm on chromium,
    # not chrome, but chromium is a barebones chrome,
    # on which chrome is built
    SELENIUM_CROME_IMAGE="seleniarm/standalone-chromium:latest"
elif [ "$(uname -m)" = "x86_64" ]; then
    echo "We are on server Ubuntu"
    # We use the regular image provided by Chrome
    SELENIUM_CROME_IMAGE="selenium/standalone-chrome:latest"
else
    echo "Error: Unsupported architecture $(uname -m), we support arm64 and x86_64."
    exit 1
fi
echo "We will use SELENIUM_CROME_IMAGE=${SELENIUM_CROME_IMAGE}."

if  docker ps | grep " $PROJECT_NAME$"; then
    echo "Container already started. Do nothing"
elif docker ps -a | grep " $PROJECT_NAME$" ; then
    docker start $PROJECT_NAME
else
    # create a container from the image, if image not present it gets downloaded first
    docker run --rm -it -d -p 4444:4444 -p 5900:5900 -p 7900:7900 \
	--name ${CONTAINER_NAME} --shm-size 2g ${SELENIUM_CROME_IMAGE}
    # create the Whatsapp profile folder to avoid scanning Whatsapp every time
    docker exec -i -t ${CONTAINER_NAME} \
	mkdir -p /home/seluser/.config/chromium/google-chrome/Whatsapp
fi