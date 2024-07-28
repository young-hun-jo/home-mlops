import json
import os
import requests

from fastapi import HTTPException
from schema.request import IrisRequest, IrisResponse


class Classifier(object):
    def __init__(self):
        self.bento_svc_name = os.getenv("BENTO_SVC_NAME", "localhost")
        self.headers = {"Content-Type": "application/json", "accept": "application/json"}
        self.bento_svc = f"http://localhost:3000/predict"

    def __call__(self, request: IrisRequest) -> IrisResponse:
        return self.forward(request)
     
    def forward(self, request: IrisRequest) -> IrisResponse:
        # preprocess
        request: list[list[float]] = self.preprocess(request)
        # prediction
        response: list[int] = self.predict_bento(request)
        # postprocess
        response: int = self.postprocess(response['response'][0][0])
        return IrisResponse(
            label=response
        )

    def preprocess(self, request: IrisRequest) -> list[list[float]]:
        return [list(request.dict().values())]
    
    def predict_bento(self, request: list[list[float]]) -> list[int]:
        resp = requests.post(
            url=self.bento_svc, 
            headers=self.headers, 
            data=json.dumps({"x": request}))
        
        if resp.status_code != 200:
            raise HTTPException(f"Error occured from BentoML Serving API: status-code: {resp.status_code}")
        return resp.json()
    
    def postprocess(self, label: float) -> int:
        # apply business logic anything
        return 1 if label > 0.5 else 0


classifier = Classifier()
