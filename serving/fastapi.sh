#!/bin/bash
LOGGER=$(date '+%Y-%m-%d %H:%M:%S')

# args
export APP_NAME="$1"
export FASTAPI_AR_NAME="$2"

# envs
export ROOT_DIR=$(git rev-parse --show-toplevel)
export HASH_TAG=$(openssl rand -base64 12)
export FASTAPI_SVC_NAME="$APP_NAME"-fastapi-svc
export FASTAPI_IMAGE_NAME=$FASTAPI_AR_NAME:$FASTAPI_SVC_NAME-$HASH_TAG
export BENTO_SVC_NAME="$APP_NAME"-bento-svc

# dockerize fastapi image
docker build \
-t $FASTAPI_IMAGE_NAME \
--build-arg FASTAPI_SVC_NAME=$FASTAPI_SVC_NAME \
--build-arg BENTO_SVC_NAME=$BENTO_SVC_NAME \
$ROOT_DIR/serving/$APP_NAME/fast-api

echo $LOGGER FASTAPI_IMAGE_NAME: $FASTAPI_IMAGE_NAME

# push fastapi image to docker hub
docker push $FASTAPI_IMAGE_NAME && docker rmi $FASTAPI_IMAGE_NAME

# docker run \
# --name $SVC_NAME \
# -p 8000:8000 \
# $AR_NAME:$SVC_NAME