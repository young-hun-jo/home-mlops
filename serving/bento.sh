#!/bin/bash
LOGGER=$(date '+%Y-%m-%d %H:%M:%S')

# args
export APP_NAME="$1"
export MLFLOW_EXPERIMENT_ID="$2"
export MLFLOW_RUN_ID="$3"
export AR_NAME="$4"

# envs
export ROOT_DIR=$(git rev-parse --show-toplevel)
export BENTO_APP_DIR=$ROOT_DIR/serving/$APP_NAME/bento-ml
export BENTOML_MODEL_NAME=$APP_NAME-bento-model
export BENTOML_SVC_NAME=$APP_NAME-bento-svc

export MODEL_NAME=$(ls $BENTO_APP_DIR/$MLFLOW_RUN_ID/artifacts/)
export MODEL_URI=$BENTO_APP_DIR/$MLFLOW_RUN_ID/artifacts/$MODEL_NAME

echo -e "$LOGGER INFO:: your setting envs are:\nBENTO_APP_DIR=$BENTO_APP_DIR\nMLFLOW_EXPERIMENT_ID=$MLFLOW_EXPERIMENT_ID\nMLFLOW_RUN_ID=$MLFLOW_RUN_ID\nBENTOML_MODEL_NAME=$BENTOML_MODEL_NAME\nBENTOML_SVC_NAME=$BENTOML_SVC_NAME\nBENTOML_AR_NAME=$AR_NAME\nMLFLOW_MODEL_URI=$MODEL_URI\n"

# function for updating package dependency based on requirements from mlflow artifacts
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

# validate path of mlflow artifacts for bento
if ! [ -d "$MODEL_URI" ]; then
    echo $LOGGER ERROR:: artifact directory does not exist: "$MODEL_URI"
    exit 99
else
    echo $LOGGER INFO:: artifact direcotry exists: "$MODEL_URI"
    requirements_path=$MODEL_URI/requirements.txt
fi

# validate configuration `bentofile` for
bentofile=$(ls $BENTO_APP_DIR | grep -E "(bentofile.yaml|bentofile.yml)")
bentofile_path=$BENTO_APP_DIR/$bentofile
if [ -z "$bentofile" ]; then
    echo $LOGGER ERROR:: bentofile does not exist for building bento
    exit 96
else
    echo $LOGGER INFO:: bentofile exists. path is $bentofile_path
fi

#================================================================
# build bento, containerize it and push it to container registry
#================================================================
# save mlflow-trained model to bento-ml Model Store 
python $BENTO_APP_DIR/import.py --bentoml_model_name="$BENTOML_MODEL_NAME" --model_uri="$MODEL_URI" && echo "$LOOGER BENTOML MODEL STORE" && ls -l $HOME/bentoml/models && \
# update `models` and `python.packages` info in bentofile configuration
tmp="${BENTOML_MODEL_NAME}:latest" yq e --inplace '.models[0] = env(tmp)' $bentofile_path && \
updatePkgOfBentofileYaml $requirements_path $bentofile_path && \
# build bento
bentoml build -f $bentofile_path && \
# conatinerize bento to docker image
bentoml containerize $BENTOML_SVC_NAME:latest && echo "zedd-debug-error: $BENTOML_SVC_NAME" 
bentoml list | grep -E $APP_NAME
bentoml_img_tag=$(bentoml list | grep -E "$BENTOML_SVC_NAME" | sort -r -k 4 | head -n 1 | awk '{print $1}') && echo $LOGGER BENTOML_TAG_NAME: $bentoml_img_tag && \
# rename tagname of docker image for pushing to docker hub registry
rename_img_tag=$(echo $AR_NAME:$(echo $bentoml_img_tag | sed 's/:/-/')) && echo $LOGGER BENTOML_IMAGE_NAME: $rename_img_tag && \
docker image tag "$bentoml_img_tag" "$rename_img_tag" && docker rmi $bentoml_img_tag && \
docker push $rename_img_tag && docker rmi $rename_img_tag