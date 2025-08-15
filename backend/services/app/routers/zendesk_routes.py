from fastapi import APIRouter, Depends, HTTPException, Request
from typing import Any

from ..schemas.zendesk import TicketCreateRequest, TicketCreateResponse

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
