#!/bin/bash

export MLRUNS_DIR=$(git rev-parse --show-toplevel)/training/mlruns
export MLFLOW_EXPERIMENT_ID="$1"
export MLFLOW_RUN_ID="$2"
export BENTOML_MODEL_NAME="$3"
export BENTOML_SVC_NAME="$4"
export BENTOML_AR_NAME="$5"

LOGGER=$(date '+%Y-%m-%d %H:%M:%S')
echo -e "$LOGGER INFO:: your setting envs are:\nMLRUNS_DIR=$MLRUNS_DIR\nMLFLOW_EXPERIMENT_ID=$MLFLOW_EXPERIMENT_ID\nMLFLOW_RUN_ID=$MLFLOW_RUN_ID\nBENTOML_MODEL_NAME=$BENTOML_MODEL_NAME\nBENTOML_SVC_NAME=$BENTOML_SVC_NAME\nBENTOML_AR_NAME=$BENTOML_AR_NAME\n"


#=========================================================================
# find artifact path of mlflow trained model for importing it in bento-ml
#=========================================================================
if ! [ -d "$MLRUNS_DIR" ]; then
    echo $LOGGER ERROR:: mlruns directory does not exist: "$MLRUNS_DIR"
    exit 99
fi

artifact_dirname="$MLRUNS_DIR"/"$MLFLOW_EXPERIMENT_ID"/"$MLFLOW_RUN_ID"/artifacts
artifact_path=$(ls $artifact_dirname)
if [ -z "$artifact_path" ]; then
    echo $LOGGER ERROR:: artifact_path does not exist: "$artifact_path"
    exit 98
else
    model_uri="$artifact_dirname"/"$artifact_path"
    echo $LOGGER INFO:: model_uri for using in bento-ml: $model_uri
fi


# check if the container is already in use
container_id=$(docker ps -a -q -f name="${BENTOML_SVC_NAME}")
if ! [ -z "$container_id" ]; then
    echo $LOGGER ERROR: The container name $BENTOML_SVC_NAME is already in use
    exit 97
fi


#===========================================================
# build, containerize bento and run deployment in container
#===========================================================
bentofile=$(ls | grep -E "bentofile")
if [ -z "$bentofile" ]; then
    echo $LOGGER ERROR:: bentofile does not exist for building bento
    exit 96
fi
# save mlflow-trained model to bento-ml Model Store 
python import.py --bentoml_model_name="$BENTOML_MODEL_NAME" --model_uri="$model_uri" && ls -l $HOME/bentoml/models && \
# update `models` info in bentofile configuration
tmp="${BENTOML_MODEL_NAME}:latest" yq e --inplace '.models[0] = env(tmp)' $bentofile && \
# build bento
bentoml build -f $bentofile && \
# conatinerize bento to docker image
bentoml containerize $BENTOML_SVC_NAME:latest && \
bentoml_img_tag=$(bentoml list | grep -E "$BENTOML_SVC_NAME" | sort -r -k 4 | head -n 1 | awk '{print $1}') && echo $LOGGER BENTOML_TAG_NAME: $bentoml_img_tag && \
# rename tagname of docker image for pushing to docker hub registry
rename_img_tag=$(echo $BENTOML_AR_NAME:$(echo $bentoml_img_tag | sed 's/:/-/')) && echo $LOGGER DOCKER_IMAGE_TAG: $rename_img_tag && \
docker image tag "$bentoml_img_tag" "$rename_img_tag" && docker rmi $bentoml_img_tag && \
docker push $rename_img_tag && docker rmi $rename_img_tag


### docker-cli for run bento-ml serving conatiner
### docker-hub url: https://hub.docker.com/repository/docker/jo181/bentoml-serving/general
# docker run -d \
# --name $BENTOML_SVC_NAME \
# -p 8000:3000 \
# -e BENTOML_SVC_NAME=$BENTOML_SVC_NAME \
# -e BENTOML_MODEL_NAME=$BENTOML_MODEL_NAME \
# $img_tag \
# serve
