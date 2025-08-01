from fastapi import APIRouter, Depends, HTTPException
from typing import Optional

from app.config import settings
from ..models.schemas import (
    HealthResponse,
    TicketRequest,
    PredictionResponse
)
from ..services.classifier_service import ClassifierService

router = APIRouter()
classifier_service = ClassifierService()

@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health Check",
    description="Check if the API is running and healthy"
)
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "message": "Ticket Classification API is running",
        "version": settings.API_VERSION
    }

@router.post(
    "/predict",
    response_model=PredictionResponse,
    summary="Predict Ticket Category",
    description="Predict the department and priority for a given ticket description"
)
async def predict_ticket(ticket: TicketRequest):
    """
    Predict the department and priority for a ticket description.
    
    - **description**: The ticket description to be classified
    """
    try:
        department, priority = classifier_service.predict(ticket.description)
        return {
            "description": ticket.description,
            "department": department,
            "priority": priority,
            "success": True
        }
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
