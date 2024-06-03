import os
import numpy as np
import bentoml
from bentoml.io import NumpyNdarray


# envs
bentoml_svc_name = os.getenv("BENTOML_SVC_NAME")
bentoml_model_name = os.getenv("BENTOML_MODEL_NAME")


# load mlflow-trained model in bento-ml Model Store and convert it to bento-ml runner object
iris_clf_model = bentoml.mlflow.get(f"{bentoml_model_name}:latest")
iris_clf_runner = iris_clf_model.to_runner()

# Service 객체 생성 -> 데코레이터 떄와는 달리 여기서 서비스 이름을 지명
svc = bentoml.Service(
    name=bentoml_svc_name,
    runners=[iris_clf_runner]
)


def preprocessing(x: np.ndarray) -> np.ndarray:
    return x 


def postprocessing(y: np.ndarray) -> np.ndarray:
    return y


# 하나의 Service 내에서 1개의 api 생성
@svc.api(input=NumpyNdarray(), output=NumpyNdarray())
def predict(input_arr: np.ndarray) -> np.ndarray:
    # preprocess
    x = preprocessing(input_arr)

    # inference
    y = iris_clf_runner.predict.run(x)

    # postprocessing 
    result = postprocessing(y)

    return result
