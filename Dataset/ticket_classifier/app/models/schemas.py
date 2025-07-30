from pydantic import BaseModel, Field
from typing import Optional

class HealthResponse(BaseModel):
    status: str
    message: str
    version: str

class TicketRequest(BaseModel):
    description: str = Field(..., 
                           description="The ticket description to be classified",
                           min_length=10,
                           example="My email is not working and I can't access my account.")

class PredictionResponse(BaseModel):
    description: str
    department: str
    priority: str
    success: bool = True
    error: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "description": "My email is not working...",
                "department": "IT Support",
                "priority": "High",
                "success": True,
                "error": None
            }
        }
