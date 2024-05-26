#!/bin/bash

export SVC_NAME="$1"
export AR_NAME=jo181/fastapi-serving

LOGGER=$(date '+%Y-%m-%d %H:%M:%S')

# dockerize fastapi image
docker build \
-t $AR_NAME:$SVC_NAME \
--build-arg SVC_NAME=$SVC_NAME \
-f Dockerfile \
.

echo $LOGGER IMAGE_NAME: $AR_NAME:$SVC_NAME

# push fastapi image to docker hub
docker push $AR_NAME:$SVC_NAME

# docker run \
# --name $SVC_NAME \
# -p 8000:8000 \
# $AR_NAME:$SVC_NAME