import pytest 
import bentoml

from bentoml._internal.models.model import Model


def test_import_model_of_mlflow_in_bentoml():
    # 경로는 mlruns/$EXPERIMENT_ID/$RUN_ID/artifacts/$ARTIFACT_PATH 를 설정해주어야 함
    mlflow_path = "/Users/zedd.ai/home-mlops/mlruns/283184337928820717/0d83b6bdeea44e34b74f70f821aa239a/artifacts/iris_model"
    # import_model 수행 -> mlflow_path에서의 모델을 retrive 후 BentoML Model Store에 cp
    model = bentoml.mlflow.import_model(
        name="test-for-import-model-in-bentoml",
        model_uri=mlflow_path
    )
    assert isinstance(model, Model), "can't laod model by mlflow using bentoml"
    