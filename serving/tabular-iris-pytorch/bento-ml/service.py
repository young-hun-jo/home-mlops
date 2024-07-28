import os
import torch
import numpy as np
import bentoml
from bentoml.validators import Shape, DType

from typing import Annotated
from pydantic import BaseModel, Field


# envs
bentoml_svc_name = os.getenv("BENTOML_SVC_NAME", "tabular-iris-pytorch-v1-bento-svc")
bentoml_model_name = os.getenv("BENTOML_MODEL_NAME", "tabular-iris-pytorch-v1-bento-model")


# load mlflow-trained model in bento-ml Model Store and convert it to bento-ml runner object
iris_clf_model = bentoml.mlflow.get(f"{bentoml_model_name}:latest")
iris_clf_runner = iris_clf_model.to_runner()
iris_clf_runner_svc = bentoml.runner_service(runner=iris_clf_runner)


@bentoml.service(
    resources={"cpu": "2"},
    traffic={"timeout": 10},
    name=bentoml_svc_name
)
class TorchRegressor:
    runner = bentoml.depends(iris_clf_runner_svc)

    @bentoml.api
    def predict(self,
                x: Annotated[np.ndarray, Shape((-1, 4)), DType("float32")] = Field(description="input torch tensor")  # 배치로 하려면 반드시 Shape에 -1 설정해주어야 함. 그리고 모델 학습시킬 때 어떤 dtype으로 학습시켰나에 따라 np.ndarray가 올지 다른게 올지 달라짐
    ) -> dict[str, np.ndarray]:
        x = self.preprocess(x)
        y = self.runner.predict(x)
        print(">>> type y:", type(y))
        return {"response": y}
    
    def preprocess(self, x):
        return x