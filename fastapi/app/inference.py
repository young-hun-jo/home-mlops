import requests
import json

from schema import IrisRequest, IrisResponse


def preprocess(request: IrisRequest) -> list[list[float]]:
    return [list(request.dict().values())]


def post_to_bentoml(request: list[list[float]]) -> list[int]:
    headers = {"Content-Type": "application/json", "accept": "application/json"}
    url = "http://bento:3000/predict"
    response = requests.post(url=url, headers=headers, data=json.dumps(request))
    if response.status_code != 200:
        return [999999]
    return response.json()


def postprocess(label: int):
    # apply business logic anything

    return label


def infer(request: IrisRequest) -> IrisResponse:
    request: list[list[float]] = preprocess(request)
    response: list[int] = post_to_bentoml(request)
    response: int = postprocess(response[0])
    return IrisResponse(
        label=response
    )
