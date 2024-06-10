#!/bin/bash

export CUSTOM_MLFLOW_BACKEND_STORE_URI=$(git rev-parse --show-toplevel)/training/mlruns
export CUSTOM_DEFAULT_ARTIFACT_ROOT_URI=$1

mlflow ui \
--backend-store-uri $CUSTOM_MLFLOW_BACKEND_STORE_URI \
--default-artifact-root $CUSTOM_DEFAULT_ARTIFACT_ROOT_URI \
--host 0.0.0.0 \
--port 8001
