# RouteIQ Ticket Management API

This is a FastAPI-based API for managing tickets across multiple ticketing platforms (Zammad and Zendesk).

## Features

- **Unified API** for multiple ticketing platforms
- **Ticket Management** - Create, read, update, and delete tickets
- **Priority Classification** - AI-powered ticket priority classification
- **Group Management** - List and manage groups
- **Health Checks** - Verify integration status with each platform

## Prerequisites

- Python 3.7+
- pip (Python package manager)
- Access to Zammad and/or Zendesk accounts with API credentials

## Installation

1. Clone the repository
2. Navigate to the `fastapi_app` directory
3. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
5. Create a `.env` file in the `fastapi_app` directory with your credentials:
   ```
   # Zammad
   ZAMMAD_URL=your_zammad_url
   ZAMMAD_EMAIL=your_email@example.com
   ZAMMAD_PASSWORD=your_password
   
   # Zendesk
   ZENDESK_EMAIL=your_email@example.com
   ZENDESK_TOKEN=your_api_token
   ZENDESK_SUBDOMAIN=your_subdomain
   ```

## Running the Application

Start the FastAPI development server:

```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

## API Documentation

Once the server is running, you can access:

- **Interactive API Docs (Swagger UI)**: http://localhost:8000/docs
- **Alternative API Docs (ReDoc)**: http://localhost:8000/redoc

## API Endpoints

### Health Check
- `GET /api/v1/health` - Check API status
- `GET /api/v1/zammad/health` - Check Zammad integration status
- `GET /api/v1/zendesk/health` - Check Zendesk integration status

### Tickets
- `POST /api/v1/zammad/tickets` - Create a new Zammad ticket
- `POST /api/v1/zendesk/tickets` - Create a new Zendesk ticket
- `GET /api/v1/zammad/tickets` - List all Zammad tickets
- `GET /api/v1/zendesk/tickets` - List all Zendesk tickets

### Classification (Groups/dept and priority)
- `GET /api/v1/zammad/classify?description=your+description` - Classify ticket priority and department (Zammad)
- `GET /api/v1/zendesk/classify?description=your+description` - Classify ticket priority and group (Zendesk)
  - Returns both `priority` (string) and `group` (string) in the response
  - Priority values: 'low'/'Low', 'normal'/'Normal'/'medium'/'Medium', 'high'/'High' (case-insensitive)
  - Group values: Matches existing group names in your Zendesk instance (case-insensitive)

### Groups
- `GET /api/v1/zammad/groups` - List all Zammad groups
- `GET /api/v1/zendesk/groups` - List all Zendesk groups

## Example Requests

### Create a Zammad Ticket with Classification
```bash
# First, get classification
curl 'http://localhost:8000/api/v1/zammad/classify?description=My+printer+is+not+working'

# Response: {"priority": "high", "group": "IT Support"}

# Then create ticket with the classified values
curl -X 'POST' \
  'http://localhost:8000/api/v1/zammad/tickets' \
  -H 'Content-Type: application/json' \
  -d '{
    "title": "Printer Not Working",
    "description": "My printer is not working and I have an important deadline.",
    "customer_email": "user@example.com",
    "priority": "high",
    "group": "IT Support"
  }'
```

### Create a Zendesk Ticket with Classification
```bash
# First, get classification
curl 'http://localhost:8000/api/v1/zendesk/classify?description=Need+help+with+my+account+access'

# Response: {"priority": "normal", "group": "Customer Support"}

# Then create ticket with the classified values
curl -X 'POST' \
  'http://localhost:8000/api/v1/zendesk/tickets' \
  -H 'Content-Type: application/json' \
  -d '{
    "subject": "Account Access Issue",
    "description": "I cannot access my account. Please help!",
    "requester_email": "user@example.com",
    "priority": "normal",
    "group": "Customer Support"
  }'
```

## Priority Mapping

The API handles priority mapping automatically:
- **Low Priority**: Mapped to priority_id 1
- **Normal/Medium Priority**: Mapped to priority_id 2 (default)
- **High Priority**: Mapped to priority_id 3

Both lowercase and capitalized values are supported (e.g., 'high' or 'High').

## Group/Department Handling

- Groups are automatically created if they don't exist (case-insensitive match)
- Group names are normalized before comparison
- If a group cannot be created, the ticket will be assigned to the default group

## Updating the Streamlit App

To use this API in your Streamlit app (`ticket_management_app.py`), replace the direct imports with HTTP requests to these endpoints. For example:

```python
import requests

# Instead of direct imports
# from zammad.zammad_integration import ...

# Use the API
BASE_URL = "http://localhost:8000/api/v1"

def create_ticket(platform, ticket_data):
    response = requests.post(f"{BASE_URL}/{platform}/tickets", json=ticket_data)
    response.raise_for_status()
    return response.json()
```

## Architecture / Data Flow

The frontend calls only our FastAPI. The ML classifier is embedded in the same FastAPI app. Zendesk and Zammad are wrapped by FastAPI endpoints. External network calls only occur from FastAPI to vendor APIs.

High-level
```
[User (Streamlit Frontend)]
            |
            v
 [RouteIQ FastAPI (single app)]
   - /api/v1/classifier/*   (embedded ML)
   - /api/v1/zendesk/*      (wrapper)
   - /api/v1/zammad/*       (wrapper)
            |
            v
 [External Vendor APIs: Zendesk / Zammad]
```

Create Ticket (with embedded ML classification)
```
[Frontend: POST /api/v1/{vendor}/tickets?use_ai=true]
            |
            v
[FastAPI Controller]
   - validate payload
   - call in-process classifier:
       predict(priority, department)
            |
            v
 [Classifier (in-process)]
   - model inference
   - return predictions
            |
            v
[FastAPI Controller]
   - map predictions -> vendor fields
     * priority -> priority_id
     * department -> group_id (find/create if needed)
   - call vendor SDK/API to create ticket
            |
            v
 [Vendor API (Zendesk/Zammad)]
            |
            v
[FastAPI Controller] -> normalize response/errors
            |
            v
[Frontend: show ticket ID/status]
```

Search / Update / Delete (no ML)
```
[Frontend: GET/PUT/DELETE /api/v1/{vendor}/tickets...]
            |
            v
[FastAPI Controller]
   - build vendor request
            |
            v
 [Vendor API (Zendesk/Zammad)]
            |
            v
[FastAPI Controller] -> normalize response
            |
            v
[Frontend]
```

Endpoint map (proposed)
- Classifier (embedded)
  - GET `/api/v1/classifier/health`
  - POST `/api/v1/classifier/predict` { title, description } -> { priority, department }
- Zendesk wrapper
  - POST `/api/v1/zendesk/tickets` (query: `use_ai=true|false`)
  - GET `/api/v1/zendesk/tickets` (search/filter)
  - PUT `/api/v1/zendesk/tickets/{id}`
  - DELETE `/api/v1/zendesk/tickets/{id}`
  - GET `/api/v1/zendesk/users`
- Zammad wrapper
  - POST `/api/v1/zammad/tickets` (query: `use_ai=true|false`)
  - GET `/api/v1/zammad/tickets`
  - PUT `/api/v1/zammad/tickets/{id}`
  - DELETE `/api/v1/zammad/tickets/{id}`
  - GET `/api/v1/zammad/users`

Notes
- Classifier calls are in-process (no extra network hop).
- Vendor-specific mapping (priority_id, group_id create/find) happens in the FastAPI layer before calling vendor APIs.
- Frontend should only use `/api/v1/...` endpoints — never call Zendesk/Zammad directly.

## License

This project is licensed under the MIT License.
