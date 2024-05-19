import numpy as np
import bentoml
from bentoml.io import NumpyNdarray


path = "/Users/zedd.ai/home-mlops/mlruns/283184337928820717/0d83b6bdeea44e34b74f70f821aa239a/artifacts/iris_model"
# `bentoml._internal.models.model.Model` object
iris_clf_model = bentoml.mlflow.import_model(
    name="zedd-iris-clf-in-mlflow",
    model_uri=path
)

iris_clf_runner = iris_clf_model.to_runner()

# Service 객체 생성 -> 데코레이터 떄와는 달리 여기서 서비스 이름을 지명
svc = bentoml.Service(
    name="zedd_iris_classifier",
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


""" Class object를 사용할 경우 `@bentoml.Service` 데코레이터 사용 -> 이렇게 하면 클래스 이름이 서비스 이름이 됨
from __future__ import annotations
import bentoml
from transformers import pipeline


EXAMPLE_INPUT = "Breaking News: In an astonishing turn of events, the small \
town of Willow Creek has been taken by storm as local resident Jerry Thompson's cat, \
Whiskers, performed what witnesses are calling a 'miraculous and gravity-defying leap.' \
Eyewitnesses report that Whiskers, an otherwise unremarkable tabby cat, jumped \
a record-breaking 20 feet into the air to catch a fly. The event, which took \
place in Thompson's backyard, is now being investigated by scientists for potential \
breaches in the laws of physics. Local authorities are considering a town festival \
to celebrate what is being hailed as 'The Leap of the Century."


# deployable unit 단위 = 서비스 1개 
@bentoml.service(
    resources={"cpu": "2"},
    traffic={"timeout": 10},
)
class Summarization:
    def __init__(self) -> None:
        # Load model into pipeline
        self.pipeline = pipeline('summarization')

    # 해당 데코레이터로 1개의 서비스 내에 1개의 api를 정의할 수 있음   
    @bentoml.api
    def summarize(self, text: str = EXAMPLE_INPUT) -> str:
        result = self.pipeline(text)
        return result[0]['summary_text']
"""

""" curl example
curl -X 'POST' \
  'http://localhost:3000/predict' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '[[6.1, 2.8, 4.7, 1.2]]'
"""