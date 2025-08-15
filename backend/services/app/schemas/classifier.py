from pydantic import BaseModel


class PredictRequest(BaseModel):
    description: str


class PredictResponse(BaseModel):
    priority: str
    department: str
