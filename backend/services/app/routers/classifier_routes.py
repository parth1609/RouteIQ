from fastapi import APIRouter, HTTPException, Depends
from typing import Optional
import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.append(str(project_root))

# Import the classifier service
from backend.Dataset.ticket_classifier.app.services.classifier_service import ClassifierService
from backend.Dataset.ticket_classifier.app.models.schemas import (
    HealthResponse,
    TicketRequest,
    PredictionResponse
)

router = APIRouter()
classifier_service = ClassifierService()

@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health Check",
    description="Check if the Classifier API is running and healthy"
)
async def health():
    """Health check endpoint for the classifier service."""
    try:
        # Test model loading and basic functionality
        test_text = "test ticket for health check"
        department, priority = classifier_service.predict(test_text)
        return {
            "status": "healthy",
            "message": "Ticket Classification API is running",
            "version": "1.0.0"
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Classifier service error: {str(e)}"
        )

@router.post(
    "/predict",
    response_model=PredictionResponse,
    summary="Predict Ticket Category",
    description="Predict the department and priority for a given ticket description"
)
async def predict(ticket: TicketRequest) -> PredictionResponse:
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
