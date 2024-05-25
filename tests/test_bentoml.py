import pytest 
import bentoml
import requests
import json

from bentoml._internal.models.model import Model


REASON = "unncessary-execution"


@pytest.mark.skip(reason=REASON)
def test_import_model_of_mlflow_in_bentoml():
    # 경로는 mlruns/$EXPERIMENT_ID/$RUN_ID/artifacts/$ARTIFACT_PATH 를 설정해주어야 함
    mlflow_path = "/Users/zedd.ai/home-mlops/mlruns/283184337928820717/0d83b6bdeea44e34b74f70f821aa239a/artifacts/iris_model"
    # import_model 수행 -> mlflow_path에서의 모델을 retrive 후 BentoML Model Store에 cp
    model = bentoml.mlflow.import_model(
        name="test-for-import-model-in-bentoml",
        model_uri=mlflow_path
    )
    assert isinstance(model, Model), "can't laod model by mlflow using bentoml"


def test_bentoml_api():
    # assume iris-classifier
    url = "http://localhost:8000/predict"
    headers = {"Content-Type": "application/json", "accept": "application/json"}
    data = [[1.0, 2.0, 3.0, 4.0]]
    resp = requests.post(url=url, headers=headers, data=json.dumps(data))
    assert isinstance(resp.json(), list)
    assert isinstance(resp.json()[0], int)
