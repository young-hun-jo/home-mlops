import mlflow
import json

from mlflow.models import infer_signature

from sklearn.datasets import load_iris 
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score
)

from home.utils import set_mlflow_backend_store_uri


class IrisTabularTrainer(object):
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
        model = LogisticRegression(**self.params)
        model.fit(X_train, y_train)

        # evaluate
        self.evaluate(model, X_train, X_test, y_train, y_test)

        # TO-DO: register mlflow
        model_info = self.register_mlflow(X_test, model)

    def load_dataset(self):
        X, y = load_iris(return_X_y=True)
        return X, y
    
    def set_params_of_model(self) -> dict:
        params = {
            "solver": "lbfgs",
            "max_iter": 1000,
            "multi_class": "auto",
            "random_state": self.random_state
        }
        return params
    
    def evaluate(self, model, X_train, X_test, y_train, y_test):
        train_proba = model.predict_proba(X_train)[:,1]
        train_pred = model.predict(X_train)

        test_proba = model.predict_proba(X_test)[:,1]
        test_pred = model.predict(X_test)
        # calculate metrics
        train_metrics = self.calculate_metrics(y_train, train_pred, train_proba, is_train=True)
        test_metrics = self.calculate_metrics(y_test, test_pred, test_proba, is_train=False)

        self.metrics = {**train_metrics, **test_metrics}
        
    def calculate_metrics(self, y_true, y_pred, y_proba, is_train=True) -> dict:
        acc = accuracy_score(y_true, y_pred)
        pre = precision_score(y_true, y_pred, average="micro")
        rec = recall_score(y_true, y_pred, average="micro")
        f1_s = f1_score(y_true, y_pred, average="micro")
        
        if is_train:
            key = "train"
        else:
            key = "validation"
        return {
            key: {
                "accuracy": acc,
                "precision": pre,
                "recall": rec,
                "f1-score": f1_s
            }
        }
    
    def register_mlflow(self, X_test, model):
        set_mlflow_backend_store_uri()

        mlflow.set_experiment(experiment_name=self.experiment_name)
        mlflow.set_experiment_tag("uuid", "zedd")
        with mlflow.start_run(run_name=self.run_name):
            # tag about run
            mlflow.set_tag("Training-info", "gcs test for iris-dataset")

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
                artifact_path="tabular-iris-multi-clf-dev",
                signature=signature,
                input_example=X_test,
                registered_model_name="tabular-iris-multi-clf-dev"
            )


if __name__ == "__main__":
    experiment_name = "tabular-iris-multi-clf-dev-exp"
    run_name = "tabular-iris-multi-clf-dev-run-v1"
    problem = "classification"

    trainer = IrisTabularTrainer(experiment_name, run_name, problem)
    model_info = trainer()
