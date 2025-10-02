# RouteIQ Build Check Log

This document captures how the project has been built so far: key components, setup steps, environment/configuration, APIs, integrations, ML classifier, recent bug fixes, testing, and git history snapshot. It is intended for new developers to quickly understand the system state and reproduce the setup.

## 1) Project Overview and Architecture
- __Gateway API__: FastAPI application in `backend/services/app/main.py`.
  - Loads env via `dotenv.find_dotenv(usecwd=True)`.
  - Initializes vendors in `lifespan()`: `ZendeskIntegration` and `initialize_zammad_client()`; stores them on `app.state`.
  - Registers routers:
    - `zendesk_routes` at `/api/v1/zendesk`
    - `zammad_routes` at `/api/v1/zammad`
    - `classifier_routes` at `/api/v1/classifier`
  - Health: `GET /api/v1/health` returns availability of integrations.

- __Routers__ (`backend/services/app/routers/`):
  - `zendesk_routes.py`:
    - `GET /health`
    - `POST /tickets` creates ticket; supports AI classification via integration layer.
  - `zammad_routes.py`:
    - `GET /health`
    - `GET /tickets` (preferred) and `GET /get_all_tickets` (back-compat)
    - `GET /tickets/{ticket_id}`
    - `PATCH /tickets/{ticket_id}`
    - `DELETE /tickets/{ticket_id}`
    - `POST /tickets` creates ticket (may use AI classification)
  - `classifier_routes.py`:
    - `GET /health`
    - `POST /predict` returns `{department, priority}` for ticket text

- __Vendor Integrations__:
  - `backend/zendesk/zendesk_integration.py` uses Zenpy for Zendesk and local classifier for predictions.
  - `backend/zammad/zammad_integration.py` uses `zammad_py` with robust helpers for list/get/update/delete; includes state-id based closing fallback.

- __Classifier Service__:
  - Entry via `backend/services/app/routers/classifier_routes.py`
  - Core model code under `backend/Dataset/ticket_classifier/app/`
    - Service: `services/classifier_service.py`
    - Schemas: `models/schemas.py`

- __Dependencies__: `backend/services/requirements.txt` (FastAPI, uvicorn, pydantic, python-dotenv, requests, zenpy, zammad-py, etc.)

## 2) Setup and Run
- __Python__: 3.10+ recommended.
- __Install deps__ (from repo root or `backend/services/`):
  - Example using venv:
    - Windows PowerShell
      ```powershell
      python -m venv .venv
      .venv\Scripts\Activate.ps1
      pip install -r backend/services/requirements.txt
      ```
- __Environment Variables__: Create `.env` at repo root (or loadable via cwd), including:
  - Zendesk: `ZENDESK_EMAIL`, `ZENDESK_TOKEN`, `ZENDESK_SUBDOMAIN`
  - Zammad: `ZAMMAD_URL`, plus one of `ZAMMAD_HTTP_TOKEN` or `ZAMMAD_USERNAME` and `ZAMMAD_PASSWORD`
  - Classifier: no external creds required; runs in-process as part of the API
  - Optional: database and other vendor keys as documented in `README.md` and `db.md`
- __Run API__:
  ```powershell
  python -m uvicorn backend.services.app.main:app --reload --host 127.0.0.1 --port 8000
  ```

## 3) API Endpoints (current)
- `GET /api/v1/health`
- Zendesk (`backend/services/app/routers/zendesk_routes.py`):
  - `GET /api/v1/zendesk/health`
  - `GET /api/v1/zendesk/tickets`
  - `GET /api/v1/zendesk/tickets/{ticket_id}`
  - `PATCH /api/v1/zendesk/tickets/{ticket_id}`
  - `DELETE /api/v1/zendesk/tickets/{ticket_id}`
  - `POST /api/v1/zendesk/tickets`
- Zammad (`backend/services/app/routers/zammad_routes.py`):
  - `GET /api/v1/zammad/health`
  - `GET /api/v1/zammad/tickets`
  - `GET /api/v1/zammad/tickets/{ticket_id}`
  - `PATCH /api/v1/zammad/tickets/{ticket_id}`
  - `DELETE /api/v1/zammad/tickets/{ticket_id}`
  - `POST /api/v1/zammad/tickets`
- Classifier (`backend/services/app/routers/classifier_routes.py`):
  - `GET /api/v1/classifier/health`
  - `POST /api/v1/classifier/predict`

## 4) Integration Details
- __Zendesk__ (`backend/zendesk/zendesk_integration.py`):
  - Loads creds from env and initializes Zenpy.
  - Classification: posts to local classifier API.
    - Note: code sets `self.API_URL = "http://127.0.0.1:8000/api/v1/"` then `PREDICT_URL = ".../predict"`.
    - Classifier router exposes `POST /api/v1/classifier/predict`. Ensure these align in runtime configs.
  - Ticket creation flow: searches/creates requester and assignee, ensures agent role and group membership, assigns group based on classified department, maps priority strings to Zendesk priority (lowercase).

- __Zammad__ (`backend/zammad/zammad_integration.py`):
  - `initialize_zammad_client()` validates creds and establishes client.
  - Helpers: `get_all_groups()`, `list_tickets()`, `get_ticket()`, `update_ticket()`, `delete_ticket()`.
  - Update supports multiple SDK signatures and raw HTTP fallback; state handling uses `state_id` or maps from name.
  - Delete attempts `destroy`; on failure, closes ticket by setting `state_id` to closed (auto-discovered or fallback to 4).

## 5) Classifier
- Router in `classifier_routes.py` initializes `ClassifierService` once.
- `GET /health` performs a trivial prediction to verify model loads.
- `POST /predict` returns `{ department, priority }` for a description.

## 6) Recent Fixes and Improvements

### Bug Fixes
- **Zammad Delete Functionality**
  - Fixed state update to use `state_id` instead of state name
  - Added dynamic closed state detection with fallback to ID 4
  - Improved error handling for ticket closure
  - Location: `backend/zammad/zammad_integration.py`

- **Zendesk Search**
  - Fixed `search_user` method to use correct Zenpy API format
  - Added proper handling of generator return type with `list()`
  - Location: `backend/zendesk/zendesk_integration.py`

- **Priority Mapping**
  - Fixed issue with AI classifier's lowercase priority values
  - Updated `priority_map` to handle both lowercase and capitalized values
  - Ensured consistent priority handling across the application

### Documentation
- **DEVELOPER_GUIDE.md**
  - Added comprehensive API documentation
  - Included examples for all endpoints
  - Added troubleshooting section
  - Documented webhook integration

### API Improvements
- Enhanced error messages for failed updates
- Added support for both `priority` (string) and `priority_id` (int)
- Improved article body handling with automatic defaults
- Better validation of input parameters

### Database
- Added `db.md` documenting Postgres (Supabase) strategy
- Included optional integrations:
  - pgvector for vector search
  - Redis for caching
  - OpenSearch for advanced search capabilities

## 7) Testing

### Test Coverage
- **TestSprite Backend Plan**: `testsprite_tests/testsprite_backend_test_plan.json`
  - **Total Test Cases**: 8
  - **Port**: 8000 (ensure app is running before tests)

### Test Cases
1. **TC001**: Overall health check endpoint (`/api/v1/health`)
2. **TC002**: Zendesk integration health check
3. **TC003**: Zammad integration health check  
4. **TC004**: Create Zammad ticket with AI classification
5. **TC005**: Simple classifier predict endpoint
6. **TC006**: Ticket Classification API root endpoint
7. **TC007**: Ticket Classification API health check
8. **TC008**: Ticket Classification API predict endpoint with validation

### Running Tests
```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_zammad_integration.py -v

# Run with coverage report
pytest --cov=backend tests/
```

### Test Dependencies
- pytest
- pytest-cov (for coverage reporting)
- requests-mock (for API mocking)
- python-dotenv (for environment variables)

## 8) Git Commit History (snapshot)
- Status: pending automated retrieval on this machine (prior command produced no output).
- To capture:
  ```powershell
  git rev-parse --is-inside-work-tree
  git --version
  git log --oneline -n 100
  git status -s
  git remote -v
  ```
  Paste the output into `memeory.md` (see next section) and link to this section.

## 9) Environment Snapshot (local)
- Status: pending automated retrieval.
- To capture:
  ```powershell
  python --version
  pip --version
  pip list --format=freeze
  ```

## 10) Action Items and Follow-ups

### High Priority
- [ ] **Security Hardening**
  - Review and tighten CORS settings in `backend/services/app/main.py` for production
  - Implement rate limiting for API endpoints
  - Set up proper secret management (e.g., HashiCorp Vault or AWS Secrets Manager)

### Medium Priority
- [ ] **Code Quality**
  - Add type hints to all functions and methods
  - Increase test coverage to at least 80%
  - Implement automated code formatting with Black and isort

### Low Priority
- [ ] **Documentation**
  - Add API versioning documentation
  - Create a CONTRIBUTING.md with contribution guidelines
  - Document deployment process for different environments

### Technical Debt
- [ ] **Refactoring**
  - Standardize error handling across all endpoints
  - Create base classes for common functionality
  - Implement proper logging throughout the application

### Future Enhancements
- [ ] **Features**
  - Add support for additional ticketing systems
  - Implement webhook support for real-time updates
  - Add user authentication and authorization

## 11) Bug Fix Journal (from Git/Memory)

This section documents the bugs fixed recently, the root causes, the solutions implemented, and how fixes were verified. Compiled from prior memory notes and recent code changes. If git logs are unavailable locally, see Section 8 for commands to capture them.

### A) Zammad Delete/Close Reliability
- __Problem__: Attempts to delete/close tickets failed with RecordInvalid due to using state names instead of IDs.
- __Root Cause__: Update payload used `state` (string) rather than `state_id` (int) accepted by Zammad.
- __Solution & Implementation__:
  - Updated delete/closure flow to set `state_id` instead of `state`.
  - Dynamically discovered the "closed" state ID from `ticket_state.all()`; fallback to `state_id = 4` when not found.
  - Added robust error handling and a fallback attempt to `destroy()` when update fails.
  - Key logic reference: `backend/zammad/zammad_integration.py` and UI wrapper in `backend/ticket_management_app.py` `delete_zammad_ticket()`.
- __Verification__:
  - Manually attempted closing tickets in varying states; confirmed no RecordInvalid.
  - Verified fallback path works when state discovery fails, and that errors are surfaced clearly.

### B) Zendesk Delete/Close Path Fixes
- __Problem__: Attribute error and update failures during delete/close attempts.
- __Root Cause__: Accessed `client.tickets` on wrapper instead of `client.zenpy_client.tickets`; also attempted to update closed tickets directly.
- __Solution & Implementation__:
  - Corrected client path to `client.zenpy_client.tickets`.
  - Added check: if ticket already `closed`, treat as deleted to avoid validation errors.
  - Implemented multi-step fallback: try `delete()`; if not allowed, set `status=closed`; if that fails, set `solved` then `closed`.
  - Key logic reference: `delete_zendesk_ticket()` in `backend/ticket_management_app.py` and related usage in `backend/zendesk/zendesk_integration.py`.
- __Verification__:
  - Manually tested tickets across statuses new/open/hold/solved; ensured one of the code paths achieves closure without exceptions.

### C) Priority Mapping Consistency (AI Classifier -> Systems)
- __Problem__: AI classifier returns lowercase priorities (e.g., "high"), but creation code expected capitalized forms, causing wrong priority assignment (e.g., defaulting to Normal).
- __Root Cause__: Mapping dictionary only handled capitalized keys.
- __Solution & Implementation__:
  - Updated priority mapping to support both lowercase and capitalized values:
    - Example applied in `backend/ticket_management_app.py` during Zammad payload construction and ensured Zendesk flows already use `.lower()`.
  - Representative mapping:
    - `low/Low -> 1`, `normal/Normal/medium/Medium -> 2`, `high/High -> 3`.
- __Verification__:
  - Created tickets with classifier predictions for each priority and confirmed correct `priority_id`/priority in the resulting tickets.

### D) Zendesk User Search Fix
- __Problem__: Searching by user email returned no results or errors.
- __Root Cause__: Incorrect Zenpy search format and generator handling.
- __Solution & Implementation__:
  - Used correct API: `users.search(f"email:{email}")`.
  - Wrapped generator in `list()` before indexing.
  - Implemented in `search_zendesk_tickets()` and `zendesk_integration.py` as applicable.
- __Verification__:
  - Searched for existing user emails and validated tickets retrieval via requester ID.

### E) Frontend Alignment to FastAPI (Zammad)
- __Problem__: Legacy Zammad SDK usage in Streamlit caused inconsistent behaviors and additional initialization steps.
- __Root Cause__: Frontend had mixed paths (SDK and API) leading to drift and maintenance overhead.
- __Solution & Implementation__:
  - Removed legacy SDK flows in the Streamlit app for Zammad operations and switched to FastAPI endpoints for create/list/get/update/delete.
  - Simplified UI: no SDK toggle; use `ROUTEIQ_API_BASE` for backend API calls; display raw IDs from API responses.
  - Fixed intermediate indentation/syntax issues from partial removals during refactor.
- __Verification__:
  - Smoke-tested create/list/update/delete flows against running FastAPI backend at `http://127.0.0.1:8000/api/v1`.
  - Confirmed health status rendering for Zammad FastAPI in the sidebar.

### F) Additional Streamlit Wiring: Zammad via FastAPI + Health Indicators
- __Problem__: Leftover paths in Streamlit still touched the Zammad SDK for search/list/update/delete; lack of visible API health made troubleshooting harder.
- __Root Cause__: Partial migration previously only covered create; helper methods for other operations were missing on the frontend.
- __Solution & Implementation__:
  - Added frontend FastAPI helpers in `backend/ticket_management_app.py`:
    - `fastapi_zammad_health()`
    - `fastapi_zammad_list_tickets()`
    - `fastapi_zammad_get_ticket(ticket_id)`
    - `fastapi_zammad_update_ticket(ticket_id, update_data)`
    - `fastapi_zammad_delete_ticket(ticket_id)`
  - Rewired Zammad flows to use these helpers:
    - `search_zammad_tickets()` now calls GET ticket or lists+filters via FastAPI
    - `get_all_zammad_tickets()` lists via FastAPI with optional legacy fallback
    - `update_zammad_ticket()` calls PATCH via FastAPI
    - `delete_zammad_ticket()` calls DELETE via FastAPI
  - Added sidebar health indicators:
    - Zammad: `fastapi_zammad_health()`
    - Zendesk: `fastapi_zendesk_health()`
    - Classifier: `check_classifier_health()` (existing)
- __Verification__:
  - Manual smoke tests: searched by ID/title/email, listed latest tickets, updated title/state, and deleted/closed ticket via FastAPI endpoints.
  - Sidebar shows ✅ when each backend is reachable, otherwise ⚠️ with error details.

### G) Frontend Cleanup: Remove Legacy Zendesk SDK in Search & Manage
- __Problem__: The Search & Manage tab in `backend/ticket_management_app.py` still referenced `st.session_state.zendesk_client` and Zendesk SDK helpers, creating mixed paths and potential runtime errors after the FastAPI migration.
- __Root Cause__: Partial migration left client checks and SDK-based code paths in tab3 (search/list/update/delete) for Zendesk.
- __Solution & Implementation__:
  - Removed client initialization check and any use of `zendesk_client` in tab3.
  - Set `client = None` explicitly; no SDK clients are used in the frontend.
  - Rewired conditional branches to FastAPI-only behavior:
    - Search: For `system == "Zendesk"`, show an informational message and return an empty result until FastAPI endpoints exist.
    - View All: For Zendesk, show an informational message and return an empty list (no SDK calls).
    - Update: For Zendesk, show an informational message (no SDK calls).
    - Delete: For Zendesk, show an informational message (no SDK calls).
  - Confirmed no references remain to `search_zendesk_tickets`, `get_all_zendesk_tickets`, `update_zendesk_ticket`, `delete_zendesk_ticket`, or `zendesk_client`.
  - File: `backend/ticket_management_app.py` (Search & Manage tab).
  - Commits: pending local Git snapshot on this machine.
- __Verification__:
  - Grep shows no matches for deprecated Zendesk SDK helpers or `zendesk_client` in `ticket_management_app.py`.
  - Manual smoke checks: Zammad flows continue to work via FastAPI; Zendesk sections now clearly indicate pending endpoint support without attempting SDK calls.

### H) Documentation Alignment for Frontend Cleanup
- __Problem__: `CHECK_LOG.md` needed to reflect the latest frontend cleanup steps for traceability.
- __Solution & Implementation__:
  - Appended entries G and H summarizing the problem, root cause, solution, and verification.
  - Left Git snapshot as pending due to no local output; instructions included in Section 8.
- __Verification__:
  - This file updated without removing any prior content; cross-references remain intact.

### I) Frontend Runtime 500 and Import Errors (Utilities and Path Aliases)
- __Problem__: Vite dev server crashed with 500 errors and import resolution failures from UI components. Errors referenced missing `clsx`/`tailwind-merge` for the `cn` utility and unresolved alias imports like `@/lib/utils`. Additional runtime import errors appeared for Radix UI and 3D helpers.
- __Root Cause__:
  - Missing utility deps: `clsx` and `tailwind-merge` required by `frontend/src/lib/utils.js`.
  - Path alias not registered in Vite/IDE for `@` and `@components` used across `frontend/src/components/ui/*.jsx`.
  - Further missing UI/3D libs referenced by components: `@radix-ui/react-dialog`, `@radix-ui/react-tabs`, `@radix-ui/react-label`, and `@react-three/drei`.
- __Solution & Implementation__:
  - Installed utilities: `clsx` and `tailwind-merge` (fixes `cn` util at `frontend/src/lib/utils.js`).
  - Added Vite path aliases in `frontend/vite.config.js`:
    - `@` -> `./src`
    - `@components` -> `./src/components`
  - Added `frontend/jsconfig.json` to mirror aliases for editor/tsserver.
  - Verified `cn` implementation in `frontend/src/lib/utils.js` and its use across UI components:
    - `frontend/src/components/ui/button.jsx` (uses `@radix-ui/react-slot`, `class-variance-authority`, `cn`)
    - `frontend/src/components/ui/label.jsx` (uses `@radix-ui/react-label`, `cn`)
    - `frontend/src/components/ui/dialog.jsx` (uses `@radix-ui/react-dialog`, `lucide-react`, `cn`)
    - `frontend/src/components/ui/tabs.jsx` (uses `@radix-ui/react-tabs`, `cn`)
    - `frontend/src/components/ui/select.jsx` (uses `@radix-ui/react-select`, `lucide-react`, `cn`)
  - Identified 3D components requiring Drei helpers:
    - `frontend/src/components/3d/FloatingIcon.jsx` (uses `@react-three/drei` Float)
    - `frontend/src/components/3d/Scene3D.jsx` (uses `@react-three/drei` OrbitControls, Environment, PerspectiveCamera)
- __Verification__:
  - After installing `clsx` and `tailwind-merge` and restarting `npm run dev`, 500 errors from the `cn` util were resolved.
  - Remaining errors were narrowed to missing packages listed above (Radix UI/Drei), confirming root cause isolation.
  - Next action: install `@radix-ui/react-dialog @radix-ui/react-tabs @radix-ui/react-label @react-three/drei` and restart the dev server.

### J) Header Dropdown Visibility (Sign Out Hidden)
- __Problem__: The user menu dropdown in the Header (containing "Sign Out") was clipped/hidden and not clickable when opened.
- __Root Cause__: The header container used `overflow-hidden`, which clipped absolutely positioned children extending outside the header area. The animated gradient overlay layer also could intercept mouse events.
- __Solution & Implementation__:
  - Updated `routeiq-frontend/src/components/layout/Header.jsx`:
    - Changed header container class from `overflow-hidden` to `overflow-visible` so the dropdown can render outside the header bounds.
    - Set `pointer-events-none` on the animated gradient overlay `<div>` to ensure it cannot block clicks on the dropdown.
    - Kept the dropdown menu with `z-50` so it stacks above the gradient background.
  - Code snippet (delta):
    - `overflow-hidden` -> `overflow-visible`
    - Overlay div: add `pointer-events-none`
- __Verification__:
  - Opened the user menu; the dropdown renders fully and the "Sign Out" button is visible and clickable.
  - Confirmed via DOM that the menu container (`absolute right-0 mt-2 ... z-50`) is no longer clipped by the header.

### K) TailwindCSS Lint Warnings (Unknown @tailwind at-rule)
- __Problem__: IDE/stylelint raised warnings: "Unknown at rule @tailwind" in `routeiq-frontend/src/index.css` lines 5–7.
- __Root Cause__: The CSS linter does not recognize Tailwind’s custom at-rules; with Tailwind v4, the recommended pattern is to import Tailwind via a standard CSS `@import` which the linter understands.
- __Solution & Implementation__:
  - Replaced the three at-rules with the v4 import:
    - Removed: `@tailwind base; @tailwind components; @tailwind utilities;`
    - Added: `@import "tailwindcss";`
  - Preserved all custom `@layer` base/components/utilities and appended fallback gradient/shadow/animation utilities so visuals remain consistent even if classes are not generated.
- __Verification__:
  - Lint warnings in the IDE cleared for `index.css`.
  - Frontend styles compile and render; gradients and animations present across Header, HomePage hero, Buttons, and Cards.

### L) Button Outline Variant Border Class Fix
- __Problem__: The `outline` variant of the Button component rendered without the intended border color. The class `border-brand-gradient` was used, but Tailwind border utilities require a color token, not a gradient token.
- __Root Cause__: `border-*` expects a color from the theme (e.g., `brand-mid`). `brand-gradient` is defined as a backgroundImage and cannot be applied to borders.
- __Solution & Implementation__:
  - Updated `routeiq-frontend/src/components/ui/Button.jsx` outline variant:
    - Replaced `border-brand-gradient` with `border-brand-mid`.
  - Kept gradient background variants for other button types (`default`, `success`, etc.) intact.
- __Verification__:
  - Visual check: outline button now shows a visible brand-colored border and hover state (`hover:border-brand-mid`).
  - Confirmed no console or build warnings for invalid class usage.

### M) Gradient Utilities Fallback + Tailwind Semantic Gradients
- __Problem__: Some brand gradient backgrounds and semantic gradient variants (success/warning/error/info/gray) did not render when Tailwind failed to generate those classes or during IDE-only previews.
- __Root Cause__: Reliance on generated utilities without concrete CSS fallbacks; missing semantic `backgroundImage` entries in Tailwind config for certain classes used by components.
- __Solution & Implementation__:
  - Added fallback utilities to `routeiq-frontend/src/index.css` under `@layer utilities`:
    - `bg-brand-gradient`, `bg-brand-animated`, `bg-page-gradient`, `bg-card-gradient`, `text-gradient-brand`, `shadow-brand`, `shadow-brand-lg`, `animate-gradient-shift`, `animate-pulse-brand`, and semantic `bg-*-gradient` classes.
  - Extended `routeiq-frontend/tailwind.config.js` `theme.extend.backgroundImage` with semantic gradients:
    - `success-gradient`, `warning-gradient`, `error-gradient`, `info-gradient`, `gray-gradient`.
- __Verification__:
  - Home hero, Header, Buttons, and Cards display gradients even if Tailwind’s JIT doesn’t generate a given class.
  - Animations (`animate-gradient-shift`, `animate-pulse-brand`) are visible; semantic variants render with matching shadows.
