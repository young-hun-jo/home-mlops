#!/bin/bash

export MLFLOW_UI=ghcr.io/young-hun-jo/mlflow-ui:v1

docker run -d \
--name mlflow-ui \
-p 8001:5000 \
-v $(pwd)/mlruns:/app/mlruns \
$MLFLOW_UI
