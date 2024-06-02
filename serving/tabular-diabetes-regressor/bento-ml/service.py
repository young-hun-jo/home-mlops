import bentoml
import os

from bentoml.io import NumpyNdarray
from numpy import ndarray


bento_svc_name = os.getenv("BENTOML_SVC_NAME")
bento_model_name = os.getenv("BENTOML_MODEL_NAME")
bento_model = bentoml.mlflow.get(f"{bento_model_name}:latest")
bento_runner = bento_model.to_runner()

svc = bentoml.Service(
    name=bento_svc_name,
    runners=[bento_runner]
)


def preprocess(x: ndarray) -> ndarray:
    return x 


@svc.api(input=NumpyNdarray(), output=NumpyNdarray())
def predict(x: ndarray) -> ndarray:
    x = preprocess(x)
    y = bento_runner.predict.run(x)
    return y