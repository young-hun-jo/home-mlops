from pydantic import BaseModel, Field


class IrisRequest(BaseModel):
    sepal_length: float = Field(example=5.1)
    sepal_width: float = Field(example=3.5)
    petal_length: float = Field(example=1.4)
    petal_width: float = Field(exmaple=0.2)


class IrisResponse(BaseModel):
    label: int = Field(example=1)
    