import requests
import json
from pydantic import BaseModel, EmailStr, Field, validator
from typing import List, Optional, Annotated, Literal, Dict, Any, Union
from dotenv import load_dotenv, find_dotenv
import os
import sys

# Add parent directory to path to import zammad_integration
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import functions from zammad_integration
from zammad.zammad_integration import (
    initialize_zammad_client,
    get_all_groups,
    find_or_create_customer
)

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
    firstname: str = Field(..., description="Customer first name", min_length=1, max_length=100)
    lastname: str = Field(..., description="Customer last name", min_length=1, max_length=100)
    
    @validator('firstname', 'lastname')
    def validate_name_fields(cls, v):
        v = v.strip()
        if not v:
            raise ValueError("Name fields cannot be empty")
        return v

class TicketArticle(BaseModel):
    """Pydantic model for ticket article data"""
    subject: str = Field(..., description="Subject of the article", max_length=255)
    body: str = Field(..., description="Body content of the article")
    internal: bool = Field(False, description="Whether the article is internal")

class TicketPriority(BaseModel):
    """Pydantic model for ticket priority"""
    priority: Literal["low", "normal", "high"] = Field("normal", description="Ticket priority level")
    
    @property
    def priority_id(self) -> int:
        """Convert priority string to Zammad priority ID"""
        priority_mapping = {"low": 1, "normal": 2, "high": 3}
        return priority_mapping[self.priority]

class Ticket(BaseModel):
    """Pydantic model for ticket creation"""
    title: Annotated[str, Field(..., title="Subject", description="Title of the ticket", max_length=255)]
    description: Annotated[str, Field(..., title="Description", description="Description of the ticket")]
    customer: Customer
    group_name: Optional[str] = Field(None, description="Department/group name for the ticket")
    priority: TicketPriority = Field(default_factory=TicketPriority)
    
    def to_zammad_params(self, customer_id: int, group_id: int) -> dict:
        """Convert the ticket model to Zammad API parameters"""
        return {
            "title": self.title,
            "group_id": group_id,
            "customer_id": customer_id,
            "priority_id": self.priority.priority_id,
            "article": {
                "subject": self.title,
                "body": self.description,
                "internal": False,
            },
        }

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
    """Create a ticket in Zammad using the provided ticket data"""
    try:
        # Initialize Zammad client
        client = initialize_zammad_client()
        
        # Find or create customer
        customer_id = find_or_create_customer(
            client, 
            ticket.customer.email,
            ticket.customer.firstname,
            ticket.customer.lastname
        )
        
        if not customer_id:
            return {"success": False, "error": "Failed to find or create customer"}
        
        # Get groups
        groups = get_all_groups(client)
        group_id = None
        
        # If group_name is provided, try to find it
        if ticket.group_name and ticket.group_name in groups:
            group_id = groups[ticket.group_name]
        else:
            # Try to classify the ticket if no group is specified
            classification = predict_ticket_category(ticket.description)
            if classification.success and classification.department in groups:
                group_id = groups[classification.department]
                
        # Default to first group if no match found
        if not group_id and groups:
            group_id = next(iter(groups.values()), 1)
        else:
            # Default to group ID 1 if no groups found
            group_id = 1
        
        # Create ticket using the Zammad API
        ticket_params = ticket.to_zammad_params(customer_id, group_id)
        created_ticket = client.ticket.create(params=ticket_params)
        
        return {"success": True, "ticket": created_ticket}
        
    except Exception as e:
        return {"success": False, "error": str(e)}



