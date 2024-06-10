import mlflow
import subprocess


# ref: https://stackoverflow.com/questions/63525498/how-do-i-set-a-different-local-directory-for-mlflow
def set_mlflow_backend_store_uri() -> None:
    mlflow.set_tracking_uri(f"http://localhost:8001")  # if `file://`, cannot upload artifacts to GCS


def get_git_root_path() -> str:
    cmd = "git rev-parse --show-toplevel"
    git_root_path: str = subprocess.check_output(cmd, shell=True).decode("utf-8")
    return git_root_path
