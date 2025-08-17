# RouteIQ Developer Guide

Audience: Engineers new to RouteIQ who want to understand the system quickly and contribute effectively.

Goals:
- Explain what the system does and why the architecture is structured this way.
- Show how code is organized and how components talk to each other.
- Provide practical steps to run, test, and extend the system.
- Define contribution guidelines aligned with the project rulebook.

## Quick Start
- Prereqs: Python 3.10+, pip, valid Zendesk and/or Zammad credentials.
- Create `.env` (at repo root or `backend/`) with:
  - Zendesk:
    - `ZENDESK_EMAIL=you@example.com`
    - `ZENDESK_TOKEN=your_api_token`
    - `ZENDESK_SUBDOMAIN=your_subdomain`
  - Zammad (pick one auth mode):
    - `ZAMMAD_URL=https://your.zammad.host`
    - `ZAMMAD_HTTP_TOKEN=your_personal_access_token`
    - or `ZAMMAD_USERNAME=you@example.com` and `ZAMMAD_PASSWORD=your_password`
  - Optional: `CLASSIFIER_BASE_URL=http://127.0.0.1:8000/api/v1/classifier/` (defaults to embedded classifier)
- Install deps (recommended: virtualenv):
  - From `backend/services`: `pip install -r requirements.txt`
- Run API gateway (from `backend/services/app`):
  - `uvicorn main:app --reload --host 127.0.0.1 --port 8000`
- Verify health:
  - API: `GET http://127.0.0.1:8000/api/v1/health`
  - Classifier: `GET http://127.0.0.1:8000/api/v1/classifier/health`
  - Zendesk: `GET http://127.0.0.1:8000/api/v1/zendesk/health`
  - Zammad: `GET http://127.0.0.1:8000/api/v1/zammad/health`
- Create a sample ticket:
  ```bash
  curl -X POST http://127.0.0.1:8000/api/v1/zendesk/tickets \
    -H "Content-Type: application/json" \
    -d '{
      "customer_email": "alice@example.com",
      "customer_name": "Alice",
      "assignee_email": "",
      "assignee_name": "",
      "ticket_subject": "Cannot login",
      "ticket_description": "Login fails with invalid password",
      "use_ai": true
    }'
  ```
- Port tips:
  - Change FastAPI port with `--port 8001`.
  - If using a separate classifier service, set its port (e.g., 8001) and update `CLASSIFIER_BASE_URL`.

---

## 1) What RouteIQ Does (High-Level)
RouteIQ provides a unified API gateway (FastAPI) that wraps external ticketing systems (Zendesk and Zammad) and an AI ticket classifier. The frontend talks only to this FastAPI, which orchestrates vendor-specific logic and optional AI classification.

Why this design:
- Single entrypoint for the frontend (simpler, consistent security/CORS).
- Vendor-agnostic endpoints that map to vendor APIs internally (easier to switch or add vendors).
- Embedded classifier keeps latency low and simplifies local dev; can be swapped for an external classifier via config.

---

## 2) Data Flow (ASCII)
Frontend (HTTP client)
  |
  v
FastAPI Gateway (`backend/services/app/main.py`)
  - mounts routers:
    - `/api/v1/zendesk` -> `routers/zendesk_routes.py`
    - `/api/v1/zammad` -> `routers/zammad_routes.py`
    - `/api/v1/classifier` -> `routers/classifier_routes.py`
  - initializes `app.state.zendesk = ZendeskIntegration()` and `app.state.zammad = initialize_zammad_client()`
  |
  v
Zendesk Router (`backend/services/app/routers/zendesk_routes.py`)
  - validates request via `schemas/zendesk.py`
  - calls `ZendeskIntegration.create_ticket_with_classification(...)`
  |
  v
ZendeskIntegration (`backend/zendesk/zendesk_integration.py`)
  - loads env, initializes Zenpy client
  - if `use_ai`:
      -> HTTP POST to `/api/v1/classifier/predict` (embedded classifier)
      -> maps prediction (priority, department) to Zendesk fields
  - creates/updates/searches tickets via Zenpy
  |
  v
Response -> Router -> FastAPI -> Frontend

Zammad Router (`backend/services/app/routers/zammad_routes.py`)
  - validates request via `schemas/zammad.py`
  - optionally calls embedded classifier to predict `priority`/`department`
  - finds/maps vendor-specific IDs (e.g., priority_id, group_id)
  - creates tickets via Zammad API client

---

## 3) Repository Structure (Relevant)
```
backend/
  services/
    app/
      __init__.py
      main.py                    # FastAPI app, lifespan, CORS, router mounting, health
      routers/
        __init__.py
        zendesk_routes.py        # HTTP endpoints for Zendesk wrapper
        zammad_routes.py         # HTTP endpoints for Zammad wrapper
        classifier_routes.py     # Embedded classifier endpoints (health, predict)
      schemas/
        __init__.py
        zendesk.py               # Pydantic models for Zendesk
        zammad.py                # Pydantic models for Zammad
        classifier.py            # Pydantic models for classifier
    requirements.txt
  zendesk/
    zendesk_integration.py       # Vendor-facing logic (Zenpy client, env, AI callouts)
  zammad/
    zammad_integration.py        # Zammad client init + helpers (env, groups, customers)

backend/Dataset/ticket_classifier/
  app/main.py                    # Optional separate classifier service (not required if embedded)
```

---

## 4) Key Files and Why They Matter
- `backend/services/app/main.py`
  - Central app factory. Wires CORS, routers, and initializes shared integrations in `lifespan`.
  - Why: Keeps startup concerns in one place, makes integrations available via `app.state` without global singletons.

- `backend/services/app/routers/zendesk_routes.py`
  - Public REST endpoints for Zendesk actions (create/search/etc.).
  - Why: Separates HTTP concerns (validation, status codes) from vendor logic.

- `backend/zendesk/zendesk_integration.py`
  - Talks to Zendesk via Zenpy, loads env, calls classifier if enabled, maps fields.
  - Why: Encapsulates vendor-specific behavior and shields routers from SDK details.

- `backend/services/app/routers/zammad_routes.py`
  - Public REST endpoints for Zammad actions (ticket create with optional AI classification, health).
  - Why: Mirrors Zendesk flow with Zammad-specific mapping and robust error handling.

- `backend/services/app/routers/classifier_routes.py`
  - Embedded classifier endpoints (`/health`, `/predict`).
  - Why: Local, low-latency classification for development and a clean swappable contract.

- `backend/services/app/schemas/*.py`
  - Pydantic models for request/response validation.
  - Why: Strong contracts at the API boundary; early error detection.

---

## 5) Running the Project
Environment
- Create `.env` (repo root or `backend/`) with Zendesk and/or Zammad variables (see Quick Start).

FastAPI (Gateway)
- From `backend/services/app`:
  - `uvicorn main:app --reload --host 127.0.0.1 --port 8000`

Health checks
- API: `GET http://127.0.0.1:8000/api/v1/health`
- Classifier: `GET http://127.0.0.1:8000/api/v1/classifier/health`
- Zendesk wrapper health: `GET http://127.0.0.1:8000/api/v1/zendesk/health`
- Zammad wrapper health: `GET http://127.0.0.1:8000/api/v1/zammad/health`

Separate classifier (optional)
- If you need to run it separately: change its port in `backend/Dataset/ticket_classifier/app/main.py` and set `CLASSIFIER_BASE_URL` accordingly.

Ports
- Use different ports if you run both gateway and a separate classifier.
- Default recommendation: gateway 8000, external classifier 8001.

---

## 6) Development Standards (From Global Rulebook)
Documentation
- Explain WHY for non-obvious logic with inline comments on the line above the code.
- Keep comments concise and up to date.
- Use consistent terminology and Pydantic/Docstring styles.

Build & Test
- Build: Bazel is the official build system. Add or update Bazel targets when adding modules.
- Tests: Use `pytest` for unit/integration tests; follow its best practices and naming.

---

## 7) Contributing Guide
Branching & PRs
- Create feature branches; keep PRs focused and small.
- Include a brief description of the change and rationale.

Code Style
- Prefer clear, maintainable code over cleverness.
- Add type hints and Pydantic models at API boundaries.
- Keep vendor-specific logic in `zendesk_integration.py` (or sibling modules for other vendors).

Comments & Docs
- Add WHY-focused comments for tricky logic.
- Update this guide and any README sections affected by your change.

Testing
- Add/extend pytest tests for new endpoints or flows.
- Include error-path tests (e.g., missing env, classifier down, invalid input).

Configuration
- Do not hardcode secrets. Use `.env` and document any new variables.
- Make external service URLs configurable (e.g., `CLASSIFIER_BASE_URL`).

API Changes
- Update `schemas/*.py` and routers together.
- Keep endpoints under `/api/v1/...` and document request/response shapes.

---

## 8) Common Tasks
Create a Zendesk ticket (with AI):
- `POST /api/v1/zendesk/tickets`
- Body:
```
{
  "customer_email": "alice@example.com",
  "customer_name": "Alice",
  "assignee_email": "",
  "assignee_name": "",
  "ticket_subject": "Cannot login",
  "ticket_description": "Login fails with invalid password",
  "use_ai": true
}
```

Create a Zammad ticket (with AI):
- `POST /api/v1/zammad/tickets`
- Body:
```
{
  "title": "Printer Not Working",
  "description": "My printer is not working and I have an important deadline.",
  "customer_email": "user@example.com",
  "customer_firstname": "Jane",
  "customer_lastname": "Doe",
  "use_ai": true
}
```

Add a new router (example outline):
1) Create `backend/services/app/routers/my_feature.py` with an `APIRouter()`.
2) Add Pydantic models in `backend/services/app/schemas/` if needed.
3) Mount it in `backend/services/app/main.py` with a versioned prefix.
4) Write pytest tests for the new endpoint.

---

## 9) Troubleshooting
- Zendesk health shows unavailable
  - Check `.env` location and values in `backend/.env`.
  - Restart uvicorn after edits.
- Classifier 404 from integration
  - Ensure `CLASSIFIER_BASE_URL` includes `/api/v1/classifier/` when using the embedded classifier.
- Email validation error on optional assignee
  - Empty strings are coerced to `null`; send `""` or omit.

---

## 10) Next Steps & Extensions
- Expand Zendesk endpoints: search, update, delete, users.
- Expand Zammad endpoints: search, update, delete, users.
- Replace placeholder classifier with a real model and add tests/metrics.

---

Maintainers: Add your contact or Slack channel here.
