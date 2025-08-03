import requests
import json
from pydantic import BaseModel, EmailStr, Field, validator
from typing import List, Optional, Annotated, Literal, Dict, Any, Union
from dotenv import load_dotenv, find_dotenv
import os
import sys

# Add parent directory to path to import zendesk_integration
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import functions from zendesk_integration
from zendesk.zendesk_integration import ZendeskIntegration

# FastAPI ticket classifier service URL - using the local ticket classifier API
API_URL = "http://127.0.0.1:8000/api/v1/"
PREDICT_URL = f"{API_URL}predict"
HEALTH_URL = f"{API_URL}health"

# Note: This implementation uses the local FastAPI ticket classifier service
# instead of the GROQ API for ticket classification

load_dotenv(find_dotenv())

class Customer(BaseModel):
    """Pydantic model for customer data validation"""
    email: EmailStr = Field(..., description="Customer email address")
    name: str = Field(..., description="Customer full name", min_length=1, max_length=100)
    
    @validator('name')
    def validate_name_field(cls, v):
        v = v.strip()
        if not v:
            raise ValueError("Name field cannot be empty")
        return v

class Assignee(BaseModel):
    """Pydantic model for assignee data validation"""
    email: EmailStr = Field(..., description="Assignee email address")
    name: str = Field(..., description="Assignee full name", min_length=1, max_length=100)
    
    @validator('name')
    def validate_name_field(cls, v):
        v = v.strip()
        if not v:
            raise ValueError("Name field cannot be empty")
        return v

class TicketPriority(BaseModel):
    """Pydantic model for ticket priority"""
    priority: Literal["low", "normal", "high", "urgent"] = Field("normal", description="Ticket priority level")
    
    @property
    def priority_id(self) -> str:
        """Convert priority string to Zendesk priority"""
        return self.priority

class Ticket(BaseModel):
    """Pydantic model for ticket creation"""
    subject: Annotated[str, Field(..., title="Subject", description="Subject of the ticket", max_length=255)]
    description: Annotated[str, Field(..., title="Description", description="Description of the ticket")]
    customer: Customer
    assignee: Optional[Assignee] = Field(None, description="Assignee for the ticket")
    priority: TicketPriority = Field(default_factory=TicketPriority)
    
    def to_zendesk_params(self, customer_id: int, assignee_id: Optional[int] = None) -> dict:
        """Convert the ticket model to Zendesk API parameters"""
        params = {
            "subject": self.subject,
            "description": self.description,
            "requester_id": customer_id,
            "priority": self.priority.priority_id,
        }
        
        if assignee_id:
            params["assignee_id"] = assignee_id
            
        return params

class ClassificationResponse(BaseModel):
    """Pydantic model for ticket classification response"""
    Department: str
    Priority: str
    error: Optional[str] = None

class TicketClassifierRequest(BaseModel):
    """Pydantic model for ticket classifier API request"""
    description: str = Field(..., min_length=10)

class TicketClassifierResponse(BaseModel):
    """Pydantic model for ticket classifier API response"""
    description: str
    department: str
    priority: str
    success: bool = True
    error: Optional[str] = None

# API Functions
def check_classifier_health() -> Dict[str, Any]:
    """Check if the ticket classifier API is healthy"""
    try:
        response = requests.get(HEALTH_URL)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"status": "error", "message": f"Failed to connect to classifier API: {str(e)}"}

def predict_ticket_category(description: str) -> Union[TicketClassifierResponse, Dict[str, Any]]:
    """Predict ticket category using the FastAPI classifier service"""
    try:
        payload = {"description": description}
        response = requests.post(PREDICT_URL, json=payload)
        response.raise_for_status()
        return TicketClassifierResponse(**response.json())
    except requests.exceptions.RequestException as e:
        # If API call fails, return an error response
        return {
            "description": description,
            "department": "Unknown",
            "priority": "Normal",
            "success": False,
            "error": f"Failed to connect to classifier API: {str(e)}"
        }

def create_ticket(ticket: Ticket) -> Dict[str, Any]:
    """Create a ticket in Zendesk using the provided ticket data"""
    try:
        # Initialize Zendesk integration
        zendesk_integration = ZendeskIntegration()
        
        # Find or create customer
        customer = zendesk_integration.search_user(ticket.customer.email)
        if not customer:
            customer = zendesk_integration.create_user(
                email=ticket.customer.email,
                name=ticket.customer.name,
                role="end-user"
            )
        
        if not customer:
            return {"success": False, "error": "Failed to find or create customer"}
        
        # Find or create assignee if provided
        assignee_id = None
        if ticket.assignee:
            assignee = zendesk_integration.search_user(ticket.assignee.email)
            if not assignee:
                assignee = zendesk_integration.create_user(
                    email=ticket.assignee.email,
                    name=ticket.assignee.name,
                    role="agent"
                )
            if assignee:
                assignee_id = assignee.id
        
        # Classify the ticket if needed
        classification = predict_ticket_category(ticket.description)
        
        # Create ticket using the Zendesk integration
        ticket_params = ticket.to_zendesk_params(customer.id, assignee_id)
        created_ticket = zendesk_integration.zenpy_client.tickets.create(**ticket_params)
        
        return {
            "success": True, 
            "ticket_id": created_ticket.ticket.id,
            "ticket_subject": created_ticket.ticket.subject,
            "ticket_status": created_ticket.ticket.status,
            "requester_email": ticket.customer.email,
            "requester_name": ticket.customer.name,
            "assignee_email": ticket.assignee.email if ticket.assignee else None,
            "assignee_name": ticket.assignee.name if ticket.assignee else None,
            "priority": ticket.priority.priority_id,
            "classification": {
                "department": classification.department if classification.success else "Unknown",
                "priority": classification.priority if classification.success else "Normal"
            },
            "message": "Ticket created successfully!"
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}

def create_ticket_with_classification(
    customer_email: str,
    customer_name: str,
    assignee_email: Optional[str] = None,
    assignee_name: Optional[str] = None,
    ticket_subject: str = "",
    ticket_description: str = ""
) -> Dict[str, Any]:
    """Create a ticket with automatic classification using FastAPI service"""
    try:
        # Initialize Zendesk integration
        zendesk_integration = ZendeskIntegration()
        
        # Classify the ticket description
        classification = predict_ticket_category(ticket_description)
        
        # Create ticket using the existing integration method
        result = zendesk_integration.create_ticket_with_classification(
            customer_email=customer_email,
            customer_name=customer_name,
            assignee_email=assignee_email,
            assignee_name=assignee_name,
            ticket_subject=ticket_subject,
            ticket_description=ticket_description,
            auto_proceed=True
        )
        
        # Add classification info to the result
        if result.get("success"):
            result["classification"] = {
                "department": classification.department if classification.success else "Unknown",
                "priority": classification.priority if classification.success else "Normal"
            }
        
        return result
        
    except Exception as e:
        return {"success": False, "error": str(e)} 