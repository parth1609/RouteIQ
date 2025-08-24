# RouteIQ

## Intelligent Ticket Routing and Management System

RouteIQ is an AI-powered ticket management system that integrates with Zammad and Zendesk to streamline IT support workflows. The system uses advanced AI classification to automatically route tickets to the appropriate departments and assign priority levels based on ticket content.

## Features

- **Unified API Gateway (FastAPI)**: Single backend at `/api/v1/...` that wraps Zendesk and Zammad, plus an embedded classifier service.
- **Multi-platform Ticketing**: Create/search/manage tickets across Zendesk and Zammad.
 
- **Optional Streamlit UI**: Simple UI for ticket creation/search built on top of the API.
- **Supabase-ready**: Documentation and schema suggestions for using Supabase (managed Postgres) with `pgvector` and Storage.
- **Health & Observability**: Health endpoints for API, classifier, and vendor adapters.
- **Flexible Auth**: Token or username/password for Zammad; token-based for Zendesk.

## Installation

### Prerequisites
- Python 3.10+
- Zammad and/or Zendesk account with API access
- ML classifer model embedded with fastapi (for AI classification)
- Database - Supabase  

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/RouteIQ.git
   cd RouteIQ
   ```

2. Install backend dependencies (recommended: use a virtualenv):
   ```bash
   pip install -r backend/services/requirements.txt
   ```

3. Create a `.env` file in the repository root with your credentials:
   ```
   # Zammad Configuration
   ZAMMAD_URL=https://your-zammad-instance.com
   ZAMMAD_HTTP_TOKEN=your_token
   # Or use username/password instead
   ZAMMAD_USERNAME=your_username
   ZAMMAD_PASSWORD=your_password

   # Zendesk Configuration
   ZENDESK_EMAIL=your_email@example.com
   ZENDESK_TOKEN=your_token
   ZENDESK_SUBDOMAIN=your_subdomain
 
   # Optional: External classifier URL (defaults to embedded)
   CLASSIFIER_BASE_URL=http://127.0.0.1:8000/api/v1/classifier/

   # Optional: Supabase (managed Postgres)
   SUPABASE_URL=https://project-id.supabase.co
   SUPABASE_ANON_KEY=your_supabase_anon_key
   SUPABASE_DB_URL=postgresql://user:pass@host:5432/postgres
   ```

## Usage

### Start the API (FastAPI Gateway)
From `backend/services/app`:
```bash
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```
Health checks:
- API: http://127.0.0.1:8000/api/v1/health
- Classifier: http://127.0.0.1:8000/api/v1/classifier/health
- Zendesk: http://127.0.0.1:8000/api/v1/zendesk/health
- Zammad: http://127.0.0.1:8000/api/v1/zammad/health

### Optional: Run the Streamlit UI
```bash
streamlit run backend/ticket_management_app.py
```
The UI will be available at http://localhost:8501 by default.

### Using the API (examples)
Create a Zendesk ticket (with AI):
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
Create a Zammad ticket (with AI):
```bash
curl -X POST http://127.0.0.1:8000/api/v1/zammad/tickets \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Printer Not Working",
    "description": "My printer is not working and I have an important deadline.",
    "customer_email": "user@example.com",
    "customer_firstname": "Jane",
    "customer_lastname": "Doe",
    "use_ai": true
  }'
```

### Using the Streamlit UI
- **Initialize Clients** in the sidebar to connect to Zendesk/Zammad.
- **Create Tickets** with optional AI classification.
- **Monitor/Search Tickets** from the history and search tabs.

## Project Structure

```
RouteIQ/
├── backend/
│  ├── services/
│  │  ├── app/
│  │  │  ├── main.py                    # FastAPI app, mounts routers, health
│  │  │  └── routers/                   # zendesk, zammad, classifier
│  │  └── requirements.txt
│  ├── zendesk/
│  │  └── zendesk_integration.py        # Zendesk SDK wrapper + AI callouts
│  ├── zammad/
│  │  └── zammad_integration.py         # Zammad client + helpers
│  └── Dataset/ticket_classifier/       # Optional separate classifier service
├── backend/ticket_management_app.py    # Optional Streamlit UI
├── DEVELOPER_GUIDE.md                  # Developer guide & API usage
└── .env                                # Environment variables (create this file)
```

## Environment Variables

| Variable | Description |
|----------|-------------|
| `ZAMMAD_URL` | URL of your Zammad instance |
| `ZAMMAD_HTTP_TOKEN` | API token for Zammad |
| `ZAMMAD_USERNAME` | Alternative authentication: username |
| `ZAMMAD_PASSWORD` | Alternative authentication: password |
| `ZENDESK_EMAIL` | Email for Zendesk authentication |
| `ZENDESK_TOKEN` | API token for Zendesk |
| `ZENDESK_SUBDOMAIN` | Your Zendesk subdomain | 
| `CLASSIFIER_BASE_URL` | Optional. External classifier base URL; defaults to embedded `/api/v1/classifier/` |
| `SUPABASE_URL` | Optional. Supabase project URL |
| `SUPABASE_ANON_KEY` | Optional. Supabase anon/public key for client SDK |
| `SUPABASE_DB_URL` | Optional. Postgres connection string for Supabase DB |

## License

This project is licensed under the MIT License - see the LICENSE file for details.