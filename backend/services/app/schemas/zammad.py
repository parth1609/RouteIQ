from typing import Optional, Dict, Any
from pydantic import BaseModel, EmailStr, Field, field_validator


class ZammadTicketCreateRequest(BaseModel):
    customer_email: EmailStr
    customer_firstname: str
    customer_lastname: str
    title: str
    description: str
    group_name: Optional[str] = None
    use_ai: bool = True

    # Allow clients to send empty strings for optional fields; coerce to None
    @field_validator("group_name", mode="before")
    @classmethod
    def empty_string_to_none(cls, v):
        if isinstance(v, str) and v.strip() == "":
            return None
        return v


class ZammadTicketCreateResponse(BaseModel):
    success: bool
    ticket: Optional[Dict[str, Any]] = None
    ticket_id: Optional[int] = None
    ticket_number: Optional[str] = None
    message: Optional[str] = None
    error: Optional[str] = None
    diagnostics: Optional[dict] = None


class ZammadHealthResponse(BaseModel):
    status: str

class ZammadTicketUpdateRequest(BaseModel):
    title: Optional[str] = None
    group_id: Optional[int] = None
    priority_id: Optional[int] = None
    customer_id: Optional[int] = None
    state_id: Optional[int] = None
    state: Optional[str] = Field(default=None, description="Optional state name; will be resolved to state_id")
    article: Optional[Dict[str, Any]] = Field(default=None, description="Optional note article to append")

    # Coerce empty strings to None
    @field_validator("title", "state", mode="before")
    @classmethod
    def empty_to_none(cls, v):
        if isinstance(v, str) and v.strip() == "":
            return None
        return v


class ZammadTicketUpdateResponse(BaseModel):
    success: bool
    ticket: Optional[Dict[str, Any]] = None
    message: Optional[str] = None
    error: Optional[str] = None


class ZammadTicketDeleteResponse(BaseModel):
    success: bool
    message: Optional[str] = None
    ticket: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
