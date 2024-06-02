from fastapi import FastAPI
from uvicorn.workers import UvicornWorker

from models.inference import regressor
from schema.request import DiabetesRequest
from schema.response import DiabetesResponse


class CustomUvicornWorker(UvicornWorker):
    CONFIG_KWARGS = {"loop": "asyncio"}
    

app = FastAPI(
    docs_url="/docs"
)


@app.get("/health_check")
def health_check():
    return {"status": "healthy"}


@app.post("/predict", response_model=DiabetesResponse)
def predict(request: DiabetesRequest):
    return regressor(request)
