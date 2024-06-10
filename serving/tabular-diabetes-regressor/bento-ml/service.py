import bentoml
from bentoml.validators import DataframeSchema

import os

from typing import Annotated
from pydantic import BaseModel, Field
import numpy as np
import pandas as pd 


bento_svc_name = os.getenv("BENTOML_SVC_NAME", "tabular-diabetes-regressor-v2-bento-svc")
bento_model_name = os.getenv("BENTOML_MODEL_NAME", "tabular-diabetes-regressor-v2-bento-model")
bento_model = bentoml.mlflow.get(f"{bento_model_name}:latest")
bento_legacy_runner = bento_model.to_runner()
bento_runner_svc = bentoml.runner_service(runner=bento_legacy_runner)
columns = ["age", "sex", "bmi", "bp", "s1", "s2", "s3", "s4", "s5", "s6"]


@bentoml.service(
    traffic={"timeout": 10},
    resources={"cpu": "2"},
    name=bento_svc_name
)
class DiabetesRegressor:
    runner = bentoml.depends(bento_runner_svc)

    @bentoml.api
    def predict(self,
                x: Annotated[pd.DataFrame, DataframeSchema(orient="records", columns=columns)] = Field(example=[{"age": 1.1, "sex": 2.2, "bmi": 3.3, "bp": 4.4, "s1": 5.5, "s2": 6.6, "s3": 7.7, "s4": 8.8, "s5": 9.9, "s6": 10.1}])
    ) -> dict[str, np.ndarray]:
        y = self.runner.predict(x)
        return {"response": y}
    