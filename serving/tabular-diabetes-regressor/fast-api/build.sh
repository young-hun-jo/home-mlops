#!/bin/bash

export APP_NAME="$1"
export FASTAPI_SVC_NAME="$APP_NAME"-fastapi-svc
export BENTO_SVC_NAME="$APP_NAME"-bento-svc
export FASTAPI_AR_NAME="$2"

LOGGER=$(date '+%Y-%m-%d %H:%M:%S')

# dockerize fastapi image
docker build \
-t $FASTAPI_AR_NAME:$FASTAPI_SVC_NAME \
--build-arg FASTAPI_SVC_NAME=$FASTAPI_SVC_NAME \
--build-arg BENTO_SVC_NAME=$BENTO_SVC_NAME \
-f Dockerfile \
.

echo $LOGGER FASTAPI_IMAGE_NAME: $FASTAPI_AR_NAME:$FASTAPI_SVC_NAME

# push fastapi image to docker hub
docker push $FASTAPI_AR_NAME:$FASTAPI_SVC_NAME && docker rmi $FASTAPI_AR_NAME:$FASTAPI_SVC_NAME

# docker run \
# --name $SVC_NAME \
# -p 8000:8000 \
# $AR_NAME:$SVC_NAME