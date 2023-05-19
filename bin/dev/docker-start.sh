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
    # for Selenium & ChromeDriver for Whatsapp:
    # --link standalone-selenium-chrome --shm-size=2g
    docker run -i -d \
            -v $HOME/.ssh:/home/jumbo/.ssh \
            -v `pwd`:/opt/$PROJECT_NAME \
            --add-host=host.docker.internal:host-gateway \
            -p 8012:8012 \
            -p 8502:8502 \
            -p 1336:1336 \
            --link standalone-selenium-chrome \
            --shm-size=2g \
            --name $PROJECT_NAME \
            -t $PROJECT_NAME:latest \
            /bin/bash
    docker exec -i -t $PROJECT_NAME poetry install
fi
