import pytest 
import mlflow


def test_log_params():
    params = {"key1": 1, "key2": {"nested_key2": 100}}

    mlflow.set_experiment("test-mlflow-exp")
    with mlflow.start_run(run_name="test-log-params"):
        mlflow.log_params(params)


def test_log_metrics():
    # metrics = {"key1": 1, "key2": {"nested_key2": 100}} # metrics dtype은 무조건 Dict[str, float]
    metrics = {"key1": 1, "key2": 100}

    mlflow.set_experiment("test-mlflow-exp")
    with mlflow.start_run(run_name="test-log-metrics"):
        mlflow.log_metrics(metrics)
