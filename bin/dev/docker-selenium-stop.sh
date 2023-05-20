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
    WHATSAPP_PROFILE_PATH="/home/seluser/.config/chromium/google-chrome"
elif [ "$(uname -m)" = "x86_64" ]; then
    echo "We are on server Ubuntu."
    # We use the regular image provided by Chrome
    WHATSAPP_PROFILE_PATH="/home/seluser/.config/chromium/google-chrome"
else
    echo "Error: Unsupported architecture $(uname -m), we support arm64 and x86_64."
    exit 1
fi
echo "We will use WHATSAPP_PROFILE_PATH=${WHATSAPP_PROFILE_PATH}."
echo "We will use Whatsapp folder F=${F}."

if  docker ps -a | grep "$CONTAINER_NAME$"; then
    # first remove the local Whatsapp folder
    rm -rf ${F}
    # first copy the Whatsapp profile from the container to the local folder
    docker cp ${CONTAINER_NAME}:${WHATSAPP_PROFILE_PATH}/${F} .
    # then actually stop the container, which for selenium also removes it
    docker stop ${CONTAINER_NAME}
    # stop will also remove it, so no need to have a line to remove
else
    echo "Container not running."
fi