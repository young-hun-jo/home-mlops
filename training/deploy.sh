#!/bin/bash

export MLFLOW_UI=ghcr.io/young-hun-jo/mlflow-ui:v1
export MLRUNS_DIR=$(git rev-parse --show-toplevel)/train/mlruns

docker run -d \
--name mlflow-ui \
-p 8001:5000 \
-v $MLRUNS_DIR:/app/mlruns \
$MLFLOW_UI
