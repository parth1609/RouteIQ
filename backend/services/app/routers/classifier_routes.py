from fastapi import APIRouter
from ..schemas.classifier import PredictRequest, PredictResponse

router = APIRouter()


@router.get("/health")
def health():
    return {"status": "ok"}


@router.post("/predict", response_model=PredictResponse)
def predict(req: PredictRequest) -> PredictResponse:
    # Simple heuristic placeholder. Replace with real model.
    text = (req.description or "").lower()
    if any(k in text for k in ["urgent", "outage", "down", "error", "failed", "critical"]):
        priority = "high"
    elif any(k in text for k in ["slow", "delay", "issue"]):
        priority = "normal"
    else:
        priority = "low"

    if any(k in text for k in ["billing", "invoice", "payment"]):
        department = "Billing"
    elif any(k in text for k in ["login", "auth", "password", "account"]):
        department = "Support"
    elif any(k in text for k in ["feature", "request", "roadmap"]):
        department = "Product"
    else:
        department = "Support"

    return PredictResponse(priority=priority, department=department)
