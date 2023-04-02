#!/bin/bash
: "${PROJECT_NAME:=template-whatsapp}"

docker exec -i -t  ${PROJECT_NAME} \
  poetry run dotenv run jupyter notebook \
  --ip="*" \
  --port=1336 \
  --NotebookApp.token=''  \
  --NotebookApp.custom_display_url=http://localhost:1336
