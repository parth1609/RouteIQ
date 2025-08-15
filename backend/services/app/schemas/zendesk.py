from typing import Optional
from pydantic import BaseModel, EmailStr, Field, field_validator


class TicketCreateRequest(BaseModel):
    customer_email: EmailStr
    customer_name: str
    assignee_email: Optional[EmailStr] = None
    assignee_name: Optional[str] = None
    subject: str = Field(..., alias="ticket_subject")
    description: str = Field(..., alias="ticket_description")
    use_ai: bool = True

    class Config:
        populate_by_name = True

    # Allow clients to send empty strings for optional fields; coerce to None
    @field_validator("assignee_email", "assignee_name", mode="before")
    @classmethod
    def empty_string_to_none(cls, v):
        if isinstance(v, str) and v.strip() == "":
            return None
        return v


class TicketCreateResponse(BaseModel):
    success: bool
    ticket_id: Optional[int] = None
    message: Optional[str] = None
    error: Optional[str] = None
    diagnostics: Optional[dict] = None


class HealthResponse(BaseModel):
    status: str
    zendesk_integration: str
