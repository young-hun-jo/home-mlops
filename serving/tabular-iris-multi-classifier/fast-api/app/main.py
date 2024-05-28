from fastapi import FastAPI
from uvicorn.workers import UvicornWorker

from models.inference import classifier
from schema.request import IrisRequest, IrisResponse


class CustomUvicornWorker(UvicornWorker):
    CONFIG_KWARGS = {"loop": "asyncio"}
    

app = FastAPI(
    docs_url="/docs",

)


@app.get("/health_check")
def health_check():
    return {"status": "healthy"}


@app.post("/predict", response_model=IrisResponse)
def predict(request: IrisRequest):
    return classifier(request)
