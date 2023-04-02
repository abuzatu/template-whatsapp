#!/bin/bash
: "${PROJECT_NAME:=template-whatsapp}"

#docker build --platform linux/amd64 --no-cache -t $PROJECT_NAME:latest .
docker build --platform linux/arm64/v8 --no-cache -t $PROJECT_NAME:latest .
