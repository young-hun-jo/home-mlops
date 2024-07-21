import json
import os
import requests

from fastapi import HTTPException
from schema.request import DiabetesRequest
from schema.response import DiabetesResponse


class Regressor(object):
    def __init__(self):
        self.bento_svc_name = os.getenv("BENTO_SVC_NAME", "localhost")
        self.headers = {"Content-Type": "application/json", "accept": "application/json"}
        self.bento_svc = "http://localhost:3000/predict"

    def __call__(self, request: DiabetesRequest) -> DiabetesResponse:
        return self.forward(request)
     
    def forward(self, request: DiabetesRequest) -> DiabetesResponse:
        # preprocess
        request: list[list[float]] = self.preprocess(request)
        # prediction
        response: list[int] = self.predict_bento(request)
        # postprocess
        response: int = self.postprocess(response[0])
        return DiabetesResponse(
            target=response
        )

    def preprocess(self, request: DiabetesRequest) -> list[list[float]]:
        return [list(request.model_dump().values())]
    
    def predict_bento(self, request: list[list[float]]) -> list[int]:
        resp = requests.post(
            url=self.bento_svc, 
            headers=self.headers, 
            data=json.dumps(request))
        
        if resp.status_code != 200:
            raise HTTPException(f"Error occured from BentoML Serving API: status-code: {resp.status_code}")
        return resp.json()
    
    def postprocess(self, label: int) -> int:
        # apply business logic anything
        return label


regressor = Regressor()
