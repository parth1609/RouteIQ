from fastapi import APIRouter, Depends, HTTPException, Request
from typing import Any
from zenpy.lib.api_objects import Ticket as ZenTicket

from ..schemas.zendesk import (
    TicketCreateRequest,
    TicketCreateResponse,
    TicketUpdateRequest,
    TicketUpdateResponse,
    TicketDeleteResponse,
)

router = APIRouter()


def get_integration(request: Request):
    integration = getattr(request.app.state, "zendesk", None)
    if not integration:
        raise HTTPException(status_code=503, detail="Zendesk integration not available (check environment credentials)")
    return integration


@router.get("/health")
def zendesk_health(request: Request) -> dict:
    ok = getattr(request.app.state, "zendesk", None) is not None
    return {"status": "ok" if ok else "unavailable"}


def _serialize_ticket(t: Any) -> dict:
    """Safely convert a Zenpy Ticket object into a JSON-serializable dict."""
    if not t:
        return {}
    def g(name: str):
        try:
            return getattr(t, name, None)
        except Exception:
            return None
    created = g("created_at")
    updated = g("updated_at")
    return {
        "id": g("id"),
        "subject": g("subject"),
        "status": g("status"),
        "priority": g("priority"),
        "requester_id": g("requester_id"),
        "assignee_id": g("assignee_id"),
        "created_at": str(created) if created is not None else None,
        "updated_at": str(updated) if updated is not None else None,
    }


@router.post("/tickets", response_model=TicketCreateResponse)
def create_ticket(payload: TicketCreateRequest, integration=Depends(get_integration)) -> Any:
    try:
        if payload.use_ai:
            result = integration.create_ticket_with_classification(
                customer_email=payload.customer_email,
                customer_name=payload.customer_name,
                assignee_email=payload.assignee_email or "",
                assignee_name=payload.assignee_name or "",
                ticket_subject=payload.subject,
                ticket_description=payload.description,
                auto_proceed=True,
            )
        else:
            # Fallback: create without AI by setting defaults inside integration
            # Reuse the same method but classifier may return Unknown; integration handles mapping
            result = integration.create_ticket_with_classification(
                customer_email=payload.customer_email,
                customer_name=payload.customer_name,
                assignee_email=payload.assignee_email or "",
                assignee_name=payload.assignee_name or "",
                ticket_subject=payload.subject,
                ticket_description=payload.description,
                auto_proceed=True,
            )

        # Normalize expected shape for response model
        if not isinstance(result, dict):
            return TicketCreateResponse(success=False, error="Unexpected integration response type")

        success = bool(result.get("success", True))
        return TicketCreateResponse(
            success=success,
            ticket_id=result.get("ticket_id"),
            message=result.get("message") or ("Ticket created successfully" if success else None),
            error=result.get("error"),
            diagnostics=result.get("diagnostics"),
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tickets")
def list_tickets(request: Request, limit: int = 50):
    """List Zendesk tickets. Optional limit parameter."""
    try:
        integration = get_integration(request)
        tickets = list(integration.zenpy_client.tickets())
        items = [_serialize_ticket(t) for t in tickets[: max(0, int(limit))]]
        return {"count": len(items), "tickets": items}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tickets/{ticket_id}")
def get_ticket(request: Request, ticket_id: int):
    """Get a Zendesk ticket by ID."""
    try:
        integration = get_integration(request)
        t = integration.zenpy_client.tickets(id=ticket_id)
        if not t:
            raise HTTPException(status_code=404, detail=f"Ticket {ticket_id} not found")
        return {"ticket": _serialize_ticket(t)}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/tickets/{ticket_id}", response_model=TicketUpdateResponse)
def update_ticket(request: Request, ticket_id: int, payload: TicketUpdateRequest):
    """Update a Zendesk ticket (partial)."""
    try:
        integration = get_integration(request)
        existing = integration.zenpy_client.tickets(id=ticket_id)
        if not existing:
            raise HTTPException(status_code=404, detail=f"Ticket {ticket_id} not found")

        update_data: dict[str, Any] = {}
        if payload.subject is not None:
            update_data["subject"] = payload.subject
        if payload.priority is not None:
            update_data["priority"] = payload.priority
        if payload.status is not None:
            update_data["status"] = payload.status
        if payload.assignee_email:
            user = integration.search_user(payload.assignee_email)
            if not user:
                raise HTTPException(status_code=400, detail=f"Assignee {payload.assignee_email} not found")
            update_data["assignee_id"] = getattr(user, "id", None)
            if not update_data["assignee_id"]:
                raise HTTPException(status_code=400, detail="Resolved assignee has no id")

        if not update_data:
            # No-op, return current state
            return TicketUpdateResponse(success=True, ticket=_serialize_ticket(existing), message="No fields to update")

        result = integration.zenpy_client.tickets.update(ZenTicket(id=ticket_id, **update_data))
        # Re-fetch to ensure we return latest state
        updated = integration.zenpy_client.tickets(id=ticket_id) or result
        return TicketUpdateResponse(success=True, ticket=_serialize_ticket(updated), message="Ticket updated")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/tickets/{ticket_id}", response_model=TicketDeleteResponse)
def delete_ticket(request: Request, ticket_id: int):
    """Delete a Zendesk ticket if possible; otherwise close it as a fallback."""
    try:
        integration = get_integration(request)
        t = integration.zenpy_client.tickets(id=ticket_id)
        if not t:
            raise HTTPException(status_code=404, detail=f"Ticket {ticket_id} not found")

        try:
            integration.zenpy_client.tickets.delete(t)
            return TicketDeleteResponse(success=True, message="Ticket deleted")
        except Exception as delete_error:
            # If already closed, consider it done
            if getattr(t, "status", None) == "closed":
                return TicketDeleteResponse(success=True, message="Ticket already closed")
            try:
                # Some instances require solving before closing
                integration.zenpy_client.tickets.update(ZenTicket(id=ticket_id, status="solved"))
            except Exception:
                pass
            try:
                integration.zenpy_client.tickets.update(ZenTicket(id=ticket_id, status="closed"))
                return TicketDeleteResponse(success=True, message="Ticket closed")
            except Exception as close_error:
                raise HTTPException(
                    status_code=500,
                    detail=f"Delete failed: {delete_error}. Close fallback failed: {close_error}",
                )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
