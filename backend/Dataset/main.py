from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Optional

from test import predict_ticket_category_loaded

app = FastAPI(title="Ticket Classification API",
             description="API for classifying support tickets into departments and priorities")

class TicketRequest(BaseModel):
    description: str = Field(..., description="The ticket description to be classified")

class TicketResponse(BaseModel):
    description: str
    department: str
    priority: str
    success: bool = True
    error: Optional[str] = None

@app.get("/", tags=["Health Check"])
async def health_check():
    """Health check endpoint to verify API is running"""
    return {"status": "healthy", "message": "Ticket Classification API is running"}

@app.post("/predict", response_model=TicketResponse, tags=["Predictions"])
async def predict_ticket(ticket: TicketRequest):
    """
    Predict the department and priority for a given ticket description.
    
    - **description**: The ticket description to be classified
    """
    try:
        # Validate input
        if not ticket.description.strip():
            raise HTTPException(status_code=400, detail="Description cannot be empty")
            
        # Get predictions
        dept, prio = predict_ticket_category_loaded(ticket.description)
        
        return {
            "description": ticket.description,
            "department": dept,
            "priority": prio,
            "success": True
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing request: {str(e)}"
        )

# # GET endpoint for browser testing (not recommended for production)
# @app.get("/predict", response_model=TicketResponse, tags=["Predictions"])
# async def predict_get(description: str):
#     """
#     GET endpoint for quick testing (not recommended for production).
#     Use POST /predict with JSON body for production use.
#     """
#     return await predict_ticket(TicketRequest(description=description))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)