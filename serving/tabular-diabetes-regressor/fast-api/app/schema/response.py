from pydantic import BaseModel, Field


class DiabetesResponse(BaseModel):
    target: float = Field(example=25)