from sklearn.datasets import load_diabetes
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

import mlflow
import json

from mlflow.models import infer_signature

from home.utils import set_mlflow_backend_store_uri


class DiabetesTabularTrainer(object):
    def __init__(
            self,
            experiment_name: str,
            run_name: str,
            problem: str
            ):
        self.experiment_name = experiment_name
        self.run_name = run_name
        self.problem = problem
        self.random_state = 42

    def __call__(self):
        model_info = self.forward()
        return model_info

    def forward(self):
        # load dataset
        X, y = self.load_dataset()
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.05, random_state=self.random_state)

        # define model and fit
        self.params = self.set_params_of_model()
        model = RandomForestRegressor(**self.params)
        model.fit(X_train, y_train)

        # evaluate
        self.evaluate(model, X_train, X_test, y_train, y_test)

        # TO-DO: register mlflow
        model_info = self.register_mlflow(X_test, model)

    def load_dataset(self):
        X, y = load_diabetes(return_X_y=True, as_frame=True)

        return X, y
    
    def set_params_of_model(self) -> dict:
        params = {
            "n_estimators": 200,
            "max_depth": 3,
            "random_state": self.random_state
        }
        return params
    
    def evaluate(self, model, X_train, X_test, y_train, y_test):
        train_pred = model.predict(X_train)
        test_pred = model.predict(X_test)

        # calculate metrics
        train_metrics = self.calculate_metrics(y_train, train_pred, is_train=True)
        test_metrics = self.calculate_metrics(y_test, test_pred, is_train=False)

        self.metrics = {**train_metrics, **test_metrics}
        
    def calculate_metrics(self, y_true, y_pred, is_train=True) -> dict:
        mse = mean_squared_error(y_true, y_pred)
        mae = mean_absolute_error(y_true, y_pred)
        r2score = r2_score(y_true, y_pred)
        
        if is_train:
            key = "train"
        else:
            key = "validation"
        return {
            key: {
                "MSE": mse,
                "MAE": mae,
                "R2-score": r2score
            }
        }
    
    def register_mlflow(self, X_test, model):
        set_mlflow_backend_store_uri()

        mlflow.set_experiment(experiment_name=self.experiment_name)
        with mlflow.start_run(run_name=self.run_name):
            # tag about run
            mlflow.set_tag("Training-info", "localhost test for diabetes-dataset")

            # params
            mlflow.log_params(self.params)
            # metrics
            mlflow.log_metrics(self.metrics["train"])
            mlflow.log_metrics(self.metrics["validation"])
            # signature
            signature = infer_signature(X_test, model.predict(X_test))
            # model
            model_info = mlflow.sklearn.log_model(
                sk_model=model,
                artifact_path="diabetes-model",
                signature=signature,
                input_example=X_test,
                registered_model_name="diabetes-regressor"
            )


if __name__ == "__main__":
    experiment_name = "tabular-diabetes-regressor-exp"
    run_name = "tabular-diabetes-regressor-run"
    problem = "regression"

    trainer = DiabetesTabularTrainer(experiment_name, run_name, problem)
    model_info = trainer()