from home.utils import set_mlflow_backend_store_uri

import mlflow
from mlflow.models import infer_signature
import numpy as np
import torch 
import torch.nn as nn
from torch.optim import SGD

from sklearn.datasets import load_iris


class Classifier(nn.Module):
    def __init__(self, X):
        super(Classifier, self).__init__()

        self.n_features = X.shape[1]

        self.l1 = nn.Linear(self.n_features, 16)
        self.l2 = nn.Linear(16, 64)
        self.l3 = nn.Linear(64, 8)
        self.l4 = nn.Linear(8, 1)
        self.relu = nn.ReLU()
        self.sigmoid = nn.Sigmoid()

    def forward(self, x):
        x = self.relu(self.l1(x))
        x = self.relu(self.l2(x))
        x = self.relu(self.l3(x))
        y = self.sigmoid(self.l4(x))
        return y


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
        self.params = {}
        self.train_metrics = {}

    def __call__(self):
        model = self.train()
        self.register_mlflow(model)
    
    def train(self) -> nn.Module:
        # load dataset
        X_np, y_np = load_iris(return_X_y=True)
        X_np, y_np = X_np.astype("float32"), y_np.astype("float32")

        # converting to tensor
        X = self.convert_ndarray_to_tensor(X_np)
        y = self.convert_ndarray_to_tensor(y_np)
        y = y.view(-1, 1)
        # model
        classifier = Classifier(X)
        optimizer = SGD(classifier.parameters())
        crtierion = nn.CrossEntropyLoss() 

        # fit
        ce = []
        epochs = 10
        for epoch in range(epochs):
            # init gradients
            optimizer.zero_grad()
            # forward
            y_pred = classifier(X)
            # loss
            loss = crtierion(y_pred, y)
            print(f"Epoch: {epoch+1} | loss:", loss.data.item())
            # backward
            loss.backward()
            # update gradients
            optimizer.step()
            ce.append(loss.data.item())
        
        self.ce = sum(ce) / len(ce)

        self.params["epochs"] = epochs
        self.train_metrics["CE-score"] = self.ce
        self.X_np = X_np[:2, :]
        self.X = X[:2, :]

        print(self.X_np.dtype, y_pred.detach().numpy().dtype)

        return classifier

    def convert_ndarray_to_tensor(self, arr):
        return torch.Tensor(arr)
    
    def register_mlflow(self, model):
        set_mlflow_backend_store_uri()

        mlflow.set_experiment(experiment_name=self.experiment_name)
        mlflow.set_experiment_tag("framework", "pytorch")
        with mlflow.start_run(run_name=self.run_name):
            mlflow.set_tag("Training-info", "localhost torch for iris-dataset")

            # params
            mlflow.log_params(self.params)
            # metrics
            mlflow.log_metrics(self.train_metrics)
            # signature
            signature = infer_signature(self.X_np, model(self.X).detach().numpy())  # `Tensor` not supported in model_input argument in `infer_signature` func
            # log model
            _ = mlflow.pytorch.log_model(
                pytorch_model=model,
                artifact_path="iris_torch_gcs",
                signature=signature,
                input_example=self.X_np,  # `Tensor` is not supported
                registered_model_name="iris-torch-gcs"
            )


if __name__ == "__main__":
    experiment_name = "tabular-iris-pytorch-v1-exp-gcs"
    run_name = "tabular-iris-pytorch-v1-run-gcs"
    problem = "classification"

    trainer = IrisTabularTrainer(experiment_name, run_name, problem)
    trainer()