from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, Any
import uvicorn
import os
from dotenv import load_dotenv
from zammad_py import ZammadAPI
import requests
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Models
class TicketCreate(BaseModel):
    """Model for creating a new ticket."""
    subject: str
    description: str
    customer_email: EmailStr
    customer_name: Optional[str] = None
    assignee_email: Optional[EmailStr] = None

class TicketResponse(BaseModel):
    """Response model for ticket creation."""
    ticket_id: int
    status: str
    message: str
    details: Optional[Dict[str, Any]] = None

# Initialize FastAPI
app = FastAPI(title="Zammad Ticket API", 
              description="API for classifying and creating Zammad tickets")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Zammad client
def get_zammad_client():
    """Initialize and return Zammad API client."""
    zammad_url = os.getenv("ZAMMAD_URL")
    http_token = os.getenv("ZAMMAD_HTTP_TOKEN")
    
    if not zammad_url:
        raise ValueError("ZAMMAD_URL environment variable is not set")
    if not http_token:
        raise ValueError("ZAMMAD_HTTP_TOKEN environment variable is not set")
    
    return ZammadAPI(url=zammad_url, http_token=http_token)

# Endpoints
@app.post("/api/tickets", response_model=TicketResponse)
async def create_ticket(ticket: TicketCreate):
    """
    Create a new ticket in Zammad with optional classification.
    
    - **subject**: Ticket subject
    - **description**: Detailed ticket description
    - **customer_email**: Email of the customer creating the ticket
    - **customer_name**: (Optional) Name of the customer
    - **assignee_email**: (Optional) Email of the agent to assign the ticket to
    """
    try:
        # Get Zammad client
        client = get_zammad_client()
        
        # Prepare ticket data
        ticket_data = {
            "title": ticket.subject,
            "customer": ticket.customer_email,
            "group": "Users",  # Default group
            "article": {
                "subject": ticket.subject,
                "body": ticket.description,
                "type": "web",
                "internal": False,
            },
            "priority": "2 normal",  # Default priority
        }
        
        # Add customer name if provided
        if ticket.customer_name:
            ticket_data["customer"] = {
                "email": ticket.customer_email,
                "firstname": ticket.customer_name.split()[0] if ticket.customer_name else "",
                "lastname": " ".join(ticket.customer_name.split()[1:]) if ticket.customer_name else "",
            }
        
        # Add assignee if provided
        if ticket.assignee_email:
            # Try to find user by email
            users = client.user.search(query=ticket.assignee_email)
            if users and len(users) > 0:
                ticket_data["owner_id"] = users[0]["id"]
        
        # Create the ticket
        result = client.ticket.create(ticket_data)
        
        return TicketResponse(
            ticket_id=result["id"],
            status="success",
            message="Ticket created successfully",
            details={"zammad_response": result}
        )
        
    except Exception as e:
        logger.error(f"Error creating ticket: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create ticket: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run("zammad_api:app", host="0.0.0.0", port=8000, reload=True)
