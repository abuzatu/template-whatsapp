#!/bin/bash
: "${PROJECT_NAME:=template-whatsapp}"

docker build --no-cache -t $PROJECT_NAME:latest .
