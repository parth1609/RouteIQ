# RouteIQ

## Intelligent Ticket Routing and Management System

RouteIQ is an AI-powered ticket management system that integrates with Zammad and Zendesk to streamline IT support workflows. The system uses advanced AI classification to automatically route tickets to the appropriate departments and assign priority levels based on ticket content.

## Features

### Ticket Management
- **Multi-platform Support**: Seamlessly integrates with both Zammad and Zendesk ticketing systems
- **AI-powered Classification**: Automatically categorizes tickets by department and priority using Groq API
- **Unified Interface**: Manage tickets from multiple systems through a single Streamlit web application

### Customer Management
- **Customer Lookup**: Search for existing customers by email
- **Automatic Customer Creation**: Create new customer profiles when needed
- **Group Selection**: Route tickets to appropriate departments/groups

### Dashboard & Analytics
- **Ticket History**: Track all created tickets in the current session
- **Search & Filter**: Find tickets by ID, customer email, or title
- **Real-time Status**: Monitor ticket status and updates

### System Configuration
- **Environment Validation**: Verify that all required API keys and credentials are properly configured
- **Flexible Authentication**: Support for token-based or username/password authentication

## Installation

### Prerequisites
- Python 3.8 or higher
- Zammad and/or Zendesk account with API access
- Groq API key (for AI classification)

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/RouteIQ.git
   cd RouteIQ
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.env` file in the project root with your credentials:
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

   # Groq API Configuration
   GROQ_API_KEY=your_groq_api_key
   ```

## Usage

### Starting the Application

Run the Streamlit application:

```bash
streamlit run ticket_management_app.py
```

The application will be available at http://localhost:8501 by default.

### Using the Application

1. **Initialize Clients**: Click the "Initialize Clients" button in the sidebar to connect to Zammad and/or Zendesk.

2. **Create Tickets**: Fill in the ticket details in the "Create Ticket" tab. Enable AI classification to automatically determine department and priority.

3. **Monitor Tickets**: View ticket history, search for specific tickets, and manage existing tickets through the interface.

## Project Structure

```
RouteIQ/
├── ticket_management_app.py  # Main Streamlit application
├── requirements.txt          # Project dependencies
├── .env                      # Environment variables (create this file)
├── zammad/                   # Zammad integration
│   └── zammad_integration.py # Zammad API client and utilities
└── zendesk/                  # Zendesk integration
    └── zendesk_integration.py # Zendesk API client and utilities
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
| `GROQ_API_KEY` | API key for Groq (AI classification) |

## License

This project is licensed under the MIT License - see the LICENSE file for details.