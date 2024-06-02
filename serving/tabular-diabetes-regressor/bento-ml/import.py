import argparse
import bentoml


def import_mlflow_model_to_bentoml_model_store(args):
    _ = bentoml.mlflow.import_model(
        name=args.bentoml_model_name,
        model_uri=args.model_uri
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--bentoml_model_name", type=str, required=True)
    parser.add_argument("--model_uri", type=str, required=True)
    args = parser.parse_args()

    import_mlflow_model_to_bentoml_model_store(args)
