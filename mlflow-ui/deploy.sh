#!/bin/bash

export MLFLOW_UI=ghcr.io/young-hun-jo/mlflow-ui:v1

docker run -d --name mlflow-ui -p 8080:5000 $MLFLOW_UI