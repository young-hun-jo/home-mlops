#!/bin/bash

export MLFLOW_EXPERIMENT_ID="$1"
export MLFLOW_RUN_ID="$2"
export APP_NAME="$3"
export BENTOML_AR_NAME="$4"

export MLRUNS_DIR=$(git rev-parse --show-toplevel)/training/mlruns
export BENTOML_MODEL_NAME="$APP_NAME"-bento-model 
export BENTOML_SVC_NAME="$APP_NAME"-bento-svc

LOGGER=$(date '+%Y-%m-%d %H:%M:%S')
echo -e "$LOGGER INFO:: your setting envs are:\nMLRUNS_DIR=$MLRUNS_DIR\nMLFLOW_EXPERIMENT_ID=$MLFLOW_EXPERIMENT_ID\nMLFLOW_RUN_ID=$MLFLOW_RUN_ID\nBENTOML_MODEL_NAME=$BENTOML_MODEL_NAME\nBENTOML_SVC_NAME=$BENTOML_SVC_NAME\nBENTOML_AR_NAME=$BENTOML_AR_NAME\n"

# functions
updatePkgOfBentofileYaml ()
{
    requirements=$(cat < $1)
    tmp=$(yq '.python.packages' $2)
    if [ "$tmp" = null ]; then 
        echo $LOOGER ERROR:: .python.packages property must be exist in $2
        exit 95
    else 
        yq -i 'del(.python.packages[])' $2
        echo "$LOOGER INFO:: existing content of .python.packages property in $2 is removed"
        echo "################ requirements.txt ################"

        for requirement in $requirements
        do
            echo $requirement
            pkg="${requirement}" yq e -i '.python.packages = .python.packages + [env(pkg)]' $2
        done
        echo "##################################################"
        echo $LOOGER INFO:: .python.packages property is updated in $2
    fi
}


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
    requirements_path=$model_uri/requirements.txt
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
# update `models` and `python.packages` info in bentofile configuration
tmp="${BENTOML_MODEL_NAME}:latest" yq e --inplace '.models[0] = env(tmp)' $bentofile && \
updatePkgOfBentofileYaml $requirements_path $bentofile && \
# build bento
bentoml build -f $bentofile && \
# conatinerize bento to docker image
bentoml containerize $BENTOML_SVC_NAME:latest && \
bentoml_img_tag=$(bentoml list | grep -E "$BENTOML_SVC_NAME" | sort -r -k 4 | head -n 1 | awk '{print $1}') && echo $LOGGER BENTOML_TAG_NAME: $bentoml_img_tag && \
# rename tagname of docker image for pushing to docker hub registry
rename_img_tag=$(echo $BENTOML_AR_NAME:$(echo $bentoml_img_tag | sed 's/:/-/')) && echo $LOGGER BENTOML_IMAGE_NAME: $rename_img_tag && \
docker image tag "$bentoml_img_tag" "$rename_img_tag" && docker rmi $bentoml_img_tag && \
docker push $rename_img_tag && docker rmi $rename_img_tag
