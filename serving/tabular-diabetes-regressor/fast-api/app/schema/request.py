from pydantic import BaseModel, Field


class DiabetesRequest(BaseModel):
    age: float = Field(example=1.0)
    sex: float = Field(example=2.0)
    bmi: float = Field(example=3.0)
    bp: float = Field(example=4.0)
    s1: float = Field(example=5.0)
    s2: float = Field(example=6.0)
    s3: float = Field(example=7.0)
    s4: float = Field(example=8.0)
    s5: float = Field(example=9.0)
    s6: float = Field(example=10.0)