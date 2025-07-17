# RouteIQ Ticket Management System

A comprehensive Streamlit web application for managing tickets across Zammad and Zendesk platforms with AI-powered classification.

## Features

### 🎫 Ticket Management
- **Create Tickets**: Create tickets in both Zammad and Zendesk systems
- **AI Classification**: Automatic ticket classification using Groq API
- **Customer Management**: Find or create customers automatically
- **Group/Department Selection**: Choose appropriate groups for ticket routing

### 📊 Dashboard Features
- **Ticket History**: View all created tickets with timestamps
- **Search & Filter**: Search tickets by ID, email, or title
- **Real-time Status**: Monitor connection status for both systems
- **Environment Validation**: Check required environment variables

### 🔧 System Integration
- **Zammad Integration**: Full support for Zammad ticket creation and management
- **Zendesk Integration**: Complete Zendesk ticket workflow with user management
- **Dual System Support**: Switch between systems seamlessly

## Installation

1. **Install Dependencies**
   ```bash
   pip install -r requirements_streamlit.txt
   ```

2. **Set Environment Variables**
   Create a `.env` file in the project root with the following variables:

   ### Zammad Configuration
   ```env
   ZAMMAD_URL=https://your-zammad-instance.com
   ZAMMAD_HTTP_TOKEN=your_http_token
   # OR use username/password
   ZAMMAD_USERNAME=your_username
   ZAMMAD_PASSWORD=your_password
   ```

   ### Zendesk Configuration
   ```env
   ZENDESK_EMAIL=your_email@company.com
   ZENDESK_TOKEN=your_api_token
   ZENDESK_SUBDOMAIN=your_subdomain
   ```

   ### Groq API (for AI Classification)
   ```env
   GROQ_API_KEY=your_groq_api_key
   ```

## Usage

1. **Start the Application**
   ```bash
   streamlit run ticket_management_app.py
   ```

2. **Initialize Clients**
   - Use the sidebar to initialize both Zammad and Zendesk clients
   - Check connection status and environment variables

3. **Create Tickets**
   - Fill in the ticket form with required information
   - Enable AI classification for automatic priority and department assignment
   - Submit to create tickets in your chosen system

4. **Monitor and Manage**
   - View ticket history in the dedicated tab
   - Use search functionality to find specific tickets
   - Manage settings and configurations

## Application Structure

### Main Components

1. **Create Ticket Tab**
   - Ticket information form
   - Customer details input
   - System-specific options (groups for Zammad, assignee for Zendesk)
   - AI classification toggle

2. **Ticket History Tab**
   - Tabular view of all created tickets
   - Export functionality
   - Clear history option

3. **Search & Manage Tab**
   - Search by various criteria
   - Ticket management actions
   - Bulk operations (coming soon)

4. **Settings Tab**
   - Environment variable configuration
   - Application preferences
   - Notification settings

### Key Functions

- `initialize_clients()`: Initialize both Zammad and Zendesk API clients
- `create_zammad_ticket()`: Create tickets in Zammad with proper error handling
- `create_zendesk_ticket()`: Create tickets in Zendesk with user management
- `classify_ticket_description()`: AI-powered ticket classification

## Features in Detail

### AI Classification
- Uses Groq API for intelligent ticket classification
- Automatically determines priority (Low, Normal, High)
- Suggests appropriate departments
- Fallback to manual classification if AI is unavailable

### Error Handling
- Comprehensive error handling for API failures
- User-friendly error messages
- Graceful fallbacks for missing configurations
- Connection status monitoring

### Security
- Environment variable validation
- Secure credential handling
- No hardcoded API keys or passwords

## Troubleshooting

### Common Issues

1. **Client Initialization Fails**
   - Check environment variables are set correctly
   - Verify API credentials and permissions
   - Ensure network connectivity to the services

2. **Ticket Creation Errors**
   - Verify user permissions in the target system
   - Check required fields are filled
   - Ensure customer email format is valid

3. **AI Classification Not Working**
   - Verify GROQ_API_KEY is set
   - Check Groq API quota and limits
   - Classification will fall back to manual if AI fails

### Environment Variable Checklist

- [ ] ZAMMAD_URL
- [ ] ZAMMAD_HTTP_TOKEN (or USERNAME/PASSWORD)
- [ ] ZENDESK_EMAIL
- [ ] ZENDESK_TOKEN
- [ ] ZENDESK_SUBDOMAIN
- [ ] GROQ_API_KEY

## Development

### Adding New Features

1. **New Ticket Fields**: Modify the form in the Create Ticket tab
2. **Additional Systems**: Add new integration modules and update the system selector
3. **Enhanced Search**: Extend the search functionality in the Search & Manage tab

### Code Structure
```
ticket_management_app.py          # Main Streamlit application
zammad/zammad_integration.py      # Zammad API integration
zendesk/zendesk_integration.py    # Zendesk API integration
requirements_streamlit.txt        # Python dependencies
.env                             # Environment variables (create this)
```

## Support

For issues and questions:
1. Check the troubleshooting section
2. Verify environment variables and API credentials
3. Review the application logs in the Streamlit interface
4. Ensure all dependencies are installed correctly

## License

This project is part of the RouteIQ system for ticket management and routing.
