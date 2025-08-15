from typing import Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Request
import requests

from ..schemas.zammad import (
    ZammadTicketCreateRequest,
    ZammadTicketCreateResponse,
)

# Reuse integration helpers from backend package
from backend.zammad.zammad_integration import (
    get_all_groups,
    find_or_create_customer,
)

router = APIRouter()


def get_client(request: Request):
    client = getattr(request.app.state, "zammad", None)
    if not client:
        raise HTTPException(status_code=503, detail="Zammad integration not available (check environment credentials)")
    return client


@router.get("/health")
def zammad_health(request: Request) -> dict:
    ok = getattr(request.app.state, "zammad", None) is not None
    return {"status": "ok" if ok else "unavailable"}


def _classify(description: str) -> tuple[Optional[str], Optional[str]]:
    """Call embedded classifier API to get (priority, department)."""
    try:
        resp = requests.post(
            "http://127.0.0.1:8000/api/v1/classifier/predict",
            json={"description": description},
            timeout=4,
        )
        if resp.ok:
            data = resp.json()
            return data.get("priority"), data.get("department")
    except Exception:
        pass
    return None, None


@router.post("/tickets", response_model=ZammadTicketCreateResponse)
def create_ticket(payload: ZammadTicketCreateRequest, client=Depends(get_client)) -> Any:
    try:
        # Resolve or create customer
        customer_id = find_or_create_customer(
            client,
            email=payload.customer_email,
            firstname=payload.customer_firstname,
            lastname=payload.customer_lastname,
        )
        if not customer_id:
            return ZammadTicketCreateResponse(success=False, error="Unable to resolve customer", diagnostics={"stage": "find_or_create_customer"})

        # Determine group
        groups = get_all_groups(client)
        group_id = None
        chosen_group_name: Optional[str] = None

        classified_priority: Optional[str] = None
        classified_department: Optional[str] = None

        if payload.use_ai:
            classified_priority, classified_department = _classify(payload.description)

        # 1) Explicit group in payload
        if payload.group_name and payload.group_name in groups:
            chosen_group_name = payload.group_name
            group_id = groups[payload.group_name]
        # 2) Classified department
        elif classified_department and classified_department in groups:
            chosen_group_name = classified_department
            group_id = groups[classified_department]
        # 3) Fallbacks
        elif groups:
            # default to first available group
            chosen_group_name, group_id = next(iter(groups.items()))
        else:
            group_id = 1  # final fallback

        # Priority mapping
        priority_map = {"low": 1, "normal": 2, "medium": 2, "high": 3}
        priority_id = 2  # default normal
        if classified_priority:
            priority_id = priority_map.get(classified_priority.lower(), 2)

        # Create ticket
        params = {
            "title": payload.title,
            "group_id": group_id,
            "customer_id": customer_id,
            "priority_id": priority_id,
            "article": {
                "subject": payload.title,
                "body": payload.description,
                "type": "note",
                "internal": False,
            },
        }

        ticket = client.ticket.create(params=params)
        ticket_id = ticket.get("id") if isinstance(ticket, dict) else None
        ticket_number = ticket.get("number") if isinstance(ticket, dict) else None

        return ZammadTicketCreateResponse(
            success=True,
            ticket=ticket if isinstance(ticket, dict) else None,
            ticket_id=ticket_id,
            ticket_number=ticket_number,
            message="Ticket created successfully",
            diagnostics={
                "group_name": chosen_group_name,
                "priority_id": priority_id,
            },
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
