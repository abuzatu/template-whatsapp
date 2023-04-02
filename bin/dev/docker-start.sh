#!/bin/bash
: "${PROJECT_NAME:=template-whatsapp}"

CONTAINER_NAME="${PROJECT_NAME}"

if  docker ps | grep " $PROJECT_NAME$"; then
    echo "Container already started. Do nothing"
elif docker ps -a | grep " $PROJECT_NAME$" ; then
    docker start $PROJECT_NAME
else
    # expose port for FastAPI: 8012
    # expose port for streamlit: 8502
    # expose port for Jupyter Notebook: 1336
    # --link selenium-chrome-debug:debug
    docker run -i -d \
            -v $HOME/.ssh:/home/jumbo/.ssh \
            -v `pwd`:/opt/$PROJECT_NAME \
            --add-host=host.docker.internal:host-gateway \
            -p 8012:8012 \
            -p 8502:8502 \
            -p 1336:1336 \
            -p 5901:5901 \
            --link standalone-chromium \
            --name $PROJECT_NAME \
            --shm-size=2g \
            -t $PROJECT_NAME:latest \
            /bin/bash
    docker exec -i -t $PROJECT_NAME poetry install
fi
