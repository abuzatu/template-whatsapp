#!/bin/bash
: "${PROJECT_NAME:=standalone-selenium-chrome}"

CONTAINER_NAME="${PROJECT_NAME}"

# the Whatsapp folder
F="Whatsapp"

# find on what machine we are, local or on server
if [ "$(uname -m)" = "arm64" ]; then
    echo "We are local on MacOS M1."
    # Chrome does not offer binaries for M1, so we need to use
    # another image, built by communty seleriarm on chromium,
    # not chrome, but chromium is a barebones chrome,
    # on which chrome is built
    SELENIUM_CROME_IMAGE="seleniarm/standalone-chromium:latest"
    WHATSAPP_PROFILE_PATH="/home/seluser/.config/chromium/google-chrome"
elif [ "$(uname -m)" = "x86_64" ]; then
    echo "We are on server Ubuntu."
    # We use the regular image provided by Chrome
    SELENIUM_CROME_IMAGE="selenium/standalone-chrome:latest"
    WHATSAPP_PROFILE_PATH="/home/seluser/.config/chromium/google-chrome"
else
    echo "Error: Unsupported architecture $(uname -m), we support arm64 and x86_64."
    exit 1
fi
echo "We will use SELENIUM_CROME_IMAGE=${SELENIUM_CROME_IMAGE}."
echo "We will use WHATSAPP_PROFILE_PATH=${WHATSAPP_PROFILE_PATH}."
echo "We will use Whatsapp folder F=${F}."

if  docker ps | grep " $PROJECT_NAME$"; then
    echo "Container already started. Do nothing"
elif docker ps -a | grep " $PROJECT_NAME$" ; then
    docker start $PROJECT_NAME
else
    # create a container from the image, if image not present it gets downloaded first
    docker run --rm -it -d -p 4444:4444 -p 5900:5900 -p 7900:7900 \
	--name ${CONTAINER_NAME} --shm-size 2g ${SELENIUM_CROME_IMAGE}
    # create the Whatsapp profile folder to avoid scanning Whatsapp every time
    # if it exists locally, copy the one from locally
    # to avoid to have to scan again the QR code and load the older messages
    if [ -d "./Whatsapp" ]; then
        echo "Folder exists, so we copy the local one in Docker."
        # first we create the folder to the path
        docker exec -i -t ${CONTAINER_NAME} mkdir -p ${WHATSAPP_PROFILE_PATH}
        # then we copy it in that path
        docker cp ${F} ${CONTAINER_NAME}:${WHATSAPP_PROFILE_PATH}
        # then give permissions of read/write to all files in the folder
        docker exec -i -t ${CONTAINER_NAME} sudo chmod -R a+rwx ${WHATSAPP_PROFILE_PATH}/${F}
        # docker exec -i -t ${CONTAINER_NAME} chown -R seluser:seluser ${WHATSAPP_PROFILE_PATH}

    else
        echo "Folder does not exist, so we recreate empty in docker."
        docker exec -i -t ${CONTAINER_NAME} mkdir -p ${WHATSAPP_PROFILE_PATH}/${F}
    fi


fi