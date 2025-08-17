from pydantic import BaseModel
from typing import Optional, Literal

class HealthResponse(BaseModel):
    """Health check response model"""
    status: str
    message: str
    version: str

class TicketRequest(BaseModel):
    """Request model for ticket prediction"""
    description: str

class PredictionResponse(BaseModel):
    """Response model for ticket prediction"""
    description: str
    department: str
    priority: str
    success: bool

# For backward compatibility
class PredictRequest(TicketRequest):
    pass

class PredictResponse(BaseModel):
    priority: str
    department: str
