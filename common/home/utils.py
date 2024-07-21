import argparse
import subprocess

import bentoml
import mlflow


# ref: https://stackoverflow.com/questions/63525498/how-do-i-set-a-different-local-directory-for-mlflow
def set_mlflow_backend_store_uri() -> None:
    mlflow.set_tracking_uri(f"http://localhost:8001")  # if `file://`, cannot upload artifacts to GCS


def get_git_root_path() -> str:
    cmd = "git rev-parse --show-toplevel"
    git_root_path: str = subprocess.check_output(cmd, shell=True).decode("utf-8")
    return git_root_path


def transplant_mlflow_model_to_bentoml_model_store(args: argparse.Namespace) -> None:
    _ = bentoml.mlflow.import_model(
        name=args.bentoml_model_name,
        model_uri=args.model_uri
    )


def transplant_mlflow_model() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bentoml_model_name", type=str, required=True)
    parser.add_argument("--model_uri", type=str, required=True)
    args = parser.parse_args()
    transplant_mlflow_model_to_bentoml_model_store(args)


def greet():
    print("Hello console script in greet!")


if __name__ == "__main__":
    greet()
