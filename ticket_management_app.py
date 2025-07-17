import streamlit as st
import os
import json
import sys
from datetime import datetime
from dotenv import load_dotenv

# Add the current directory to Python path to import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import our integration modules
from zammad.zammad_integration import initialize_zammad_client, classify_ticket_description, get_all_groups, find_or_create_customer
from zendesk.zendesk_integration import ZendeskIntegration

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="RouteIQ Ticket Management",
    page_icon="🎫",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .section-header {
        font-size: 1.5rem;
        color: #2e8b57;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    .success-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
    }
    .error-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
    }
    .info-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        color: #0c5460;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'zammad_client' not in st.session_state:
    st.session_state.zammad_client = None
if 'zendesk_client' not in st.session_state:
    st.session_state.zendesk_client = None
if 'ticket_history' not in st.session_state:
    st.session_state.ticket_history = []

def initialize_clients():
    """Initialize both Zammad and Zendesk clients"""
    try:
        # Initialize Zammad client
        if st.session_state.zammad_client is None:
            st.session_state.zammad_client = initialize_zammad_client()
            st.success("✅ Zammad client initialized successfully!")
    except Exception as e:
        st.error(f"❌ Failed to initialize Zammad client: {str(e)}")
    
    try:
        # Initialize Zendesk client
        if st.session_state.zendesk_client is None:
            st.session_state.zendesk_client = ZendeskIntegration()
            st.success("✅ Zendesk client initialized successfully!")
    except Exception as e:
        st.error(f"❌ Failed to initialize Zendesk client: {str(e)}")

def create_zammad_ticket(client, ticket_data):
    """Create a ticket in Zammad"""
    try:
        # Find or create customer
        customer_id = find_or_create_customer(
            client, 
            ticket_data['customer_email'],
            ticket_data.get('customer_firstname', ''),
            ticket_data.get('customer_lastname', '')
        )
        
        if not customer_id:
            return None, "Failed to find or create customer"
        
        # Get groups
        groups = get_all_groups(client)
        group_id = groups.get(ticket_data['group'], 1)  # Default to group 1 if not found
        
        # Classify ticket if enabled
        classification = None
        if ticket_data.get('enable_classification', False):
            classification = classify_ticket_description(ticket_data['description'])
        
        # Create ticket
        ticket_payload = {
            'title': ticket_data['title'],
            'group_id': group_id,
            'customer_id': customer_id,
            'article': {
                'subject': ticket_data['title'],
                'body': ticket_data['description'],
                'type': 'note',
                'internal': False
            }
        }
        
        # Add priority if classified
        if classification and 'Priority' in classification:
            priority_map = {'Low': 1, 'Normal': 2, 'High': 3}
            ticket_payload['priority_id'] = priority_map.get(classification['Priority'], 2)
        
        # Create the ticket
        created_ticket = client.ticket.create(ticket_payload)
        
        return created_ticket, None
        
    except Exception as e:
        return None, str(e)

def create_zendesk_ticket(client, ticket_data):
    """Create a ticket in Zendesk"""
    try:
        result = client.create_ticket_with_classification(
            customer_email=ticket_data['customer_email'],
            customer_name=f"{ticket_data.get('customer_firstname', '')} {ticket_data.get('customer_lastname', '')}".strip(),
            assignee_email=ticket_data.get('assignee_email', ''),
            assignee_name=ticket_data.get('assignee_name', ''),
            ticket_subject=ticket_data['title'],
            ticket_description=ticket_data['description'],
            auto_proceed=True  # Automatically proceed with AI classification in web context
        )
        return result, None
    except Exception as e:
        return None, str(e)

def search_zammad_tickets(client, search_type, search_query):
    """Search tickets in Zammad"""
    try:
        if search_type == "Ticket ID":
            ticket = client.ticket.find(int(search_query))
            return [ticket] if ticket else []
        elif search_type == "Customer Email":
            # Search by customer email
            tickets = client.ticket.search(query=f"customer.email:{search_query}")
            return tickets if tickets else []
        elif search_type == "Title":
            # Search by title
            tickets = client.ticket.search(query=f"title:{search_query}")
            return tickets if tickets else []
        else:
            return []
    except Exception as e:
        st.error(f"Error searching Zammad tickets: {str(e)}")
        return []

def search_zendesk_tickets(client, search_type, search_query):
    """Search tickets in Zendesk"""
    try:
        if search_type == "Ticket ID":
            ticket = client.zenpy_client.tickets(id=int(search_query))
            return [ticket] if ticket else []
        elif search_type == "Customer Email":
            # First find user by email, then get their tickets
            users = list(client.zenpy_client.users.search(f"email:{search_query}"))
            if users:
                user = users[0]
                tickets = list(client.zenpy_client.tickets(requester_id=user.id))
                return tickets
            return []
        elif search_type == "Title":
            # Search by subject
            tickets = list(client.zenpy_client.search(f"subject:{search_query}", type="ticket"))
            return tickets
        else:
            return []
    except Exception as e:
        st.error(f"Error searching Zendesk tickets: {str(e)}")
        return []

def get_all_zammad_tickets(client, limit=50):
    """Get all tickets from Zammad"""
    try:
        tickets = client.ticket.all()
        # Convert to list and limit results
        ticket_list = []
        count = 0
        for ticket in tickets:
            if count >= limit:
                break
            ticket_list.append(ticket)
            count += 1
        return ticket_list
    except Exception as e:
        st.error(f"Error fetching Zammad tickets: {str(e)}")
        return []

def get_all_zendesk_tickets(client, limit=50):
    """Get all tickets from Zendesk"""
    try:
        tickets = list(client.zenpy_client.tickets())[:limit]
        return tickets
    except Exception as e:
        st.error(f"Error fetching Zendesk tickets: {str(e)}")
        return []

def update_zammad_ticket(client, ticket_id, update_data):
    """Update a ticket in Zammad"""
    try:
        result = client.ticket.update(ticket_id, update_data)
        return result, None
    except Exception as e:
        return None, str(e)

def update_zendesk_ticket(client, ticket_id, update_data):
    """Update a ticket in Zendesk"""
    try:
        ticket = client.zenpy_client.tickets(id=ticket_id)
        for key, value in update_data.items():
            setattr(ticket, key, value)
        result = client.zenpy_client.tickets.update(ticket)
        return result, None
    except Exception as e:
        return None, str(e)

def delete_zammad_ticket(client, ticket_id):
    """Delete a ticket in Zammad"""
    try:
        result = client.ticket.destroy(ticket_id)
        return result, None
    except Exception as e:
        return None, str(e)

def delete_zendesk_ticket(client, ticket_id):
    """Delete a ticket in Zendesk"""
    try:
        result = client.zenpy_client.tickets.delete(ticket_id)
        return result, None
    except Exception as e:
        return None, str(e)

def format_ticket_for_display(ticket, system):
    """Format ticket data for display in Streamlit"""
    if system == "Zammad":
        return {
            "ID": ticket.get('id', 'N/A'),
            "Title": ticket.get('title', 'N/A'),
            "State": ticket.get('state', 'N/A'),
            "Priority": ticket.get('priority', 'N/A'),
            "Customer": ticket.get('customer', 'N/A'),
            "Group": ticket.get('group', 'N/A'),
            "Created": ticket.get('created_at', 'N/A'),
            "Updated": ticket.get('updated_at', 'N/A')
        }
    else:  # Zendesk
        return {
            "ID": getattr(ticket, 'id', 'N/A'),
            "Subject": getattr(ticket, 'subject', 'N/A'),
            "Status": getattr(ticket, 'status', 'N/A'),
            "Priority": getattr(ticket, 'priority', 'N/A'),
            "Requester ID": getattr(ticket, 'requester_id', 'N/A'),
            "Assignee ID": getattr(ticket, 'assignee_id', 'N/A'),
            "Created": getattr(ticket, 'created_at', 'N/A'),
            "Updated": getattr(ticket, 'updated_at', 'N/A')
        }

def main():
    # Header
    st.markdown('<h1 class="main-header">🎫 RouteIQ Ticket Management System</h1>', unsafe_allow_html=True)
    
    # Sidebar for system selection and configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # System selection
        system = st.selectbox(
            "Select Ticketing System",
            ["Zammad", "Zendesk"],
            help="Choose which ticketing system to use"
        )
        
        # Initialize clients button
        if st.button("🔄 Initialize Clients", type="primary"):
            initialize_clients()
        
        # Connection status
        st.subheader("🔗 Connection Status")
        if st.session_state.zammad_client:
            st.success("Zammad: Connected")
        else:
            st.error("Zammad: Not Connected")
            
        if st.session_state.zendesk_client:
            st.success("Zendesk: Connected")
        else:
            st.error("Zendesk: Not Connected")
        
        # Environment variables check
        st.subheader("🔐 Environment Variables")
        env_vars = {
            "Zammad": ["ZAMMAD_URL", "ZAMMAD_HTTP_TOKEN", "GROQ_API_KEY"],
            "Zendesk": ["ZENDESK_EMAIL", "ZENDESK_TOKEN", "ZENDESK_SUBDOMAIN", "GROQ_API_KEY"]
        }
        
        for var in env_vars[system]:
            if os.getenv(var):
                st.success(f"✅ {var}")
            else:
                st.error(f"❌ {var}")
    
    # Main content area
    tab1, tab2, tab3, tab4 = st.tabs(["📝 Create Ticket", "📊 Ticket History", "🔍 Search & Manage", "⚙️ Settings"])
    
    with tab1:
        st.markdown('<h2 class="section-header">Create New Ticket</h2>', unsafe_allow_html=True)
        
        # Check if client is initialized
        client = st.session_state.zammad_client if system == "Zammad" else st.session_state.zendesk_client
        
        if not client:
            st.warning(f"⚠️ Please initialize the {system} client first using the sidebar.")
            return
        
        # Create ticket form
        with st.form("create_ticket_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("📋 Ticket Information")
                title = st.text_input("Ticket Title*", placeholder="Brief description of the issue")
                description = st.text_area("Ticket Description*", placeholder="Detailed description of the issue", height=150)
                
                # Classification option
                enable_classification = st.checkbox("🤖 Enable AI Classification", value=True)
                
            with col2:
                st.subheader("👤 Customer Information")
                customer_email = st.text_input("Customer Email*", placeholder="customer@example.com")
                customer_firstname = st.text_input("Customer First Name", placeholder="John")
                customer_lastname = st.text_input("Customer Last Name", placeholder="Doe")
                
                if system == "Zammad":
                    # Get available groups for Zammad
                    if st.session_state.zammad_client:
                        try:
                            groups = get_all_groups(st.session_state.zammad_client)
                            group_options = list(groups.keys()) if groups else ["Users"]
                        except:
                            group_options = ["Users"]
                    else:
                        group_options = ["Users"]
                    
                    group = st.selectbox("Group/Department", group_options)
                
                elif system == "Zendesk":
                    st.info("💡 **Assignee fields are optional.** If your Zendesk account has reached the agent limit, tickets will be created without assignees.")
                    assignee_email = st.text_input("Assignee Email (Optional)", placeholder="agent@example.com")
                    assignee_name = st.text_input("Assignee Name (Optional)", placeholder="Agent Name")
            
            # Submit button
            submitted = st.form_submit_button("🎫 Create Ticket", type="primary")
            
            if submitted:
                # Validate required fields
                if not title or not description or not customer_email:
                    st.error("❌ Please fill in all required fields (marked with *)")
                    return
                
                # Prepare ticket data
                ticket_data = {
                    'title': title,
                    'description': description,
                    'customer_email': customer_email,
                    'customer_firstname': customer_firstname,
                    'customer_lastname': customer_lastname,
                    'enable_classification': enable_classification
                }
                
                if system == "Zammad":
                    ticket_data['group'] = group
                elif system == "Zendesk":
                    ticket_data['assignee_email'] = assignee_email
                    ticket_data['assignee_name'] = assignee_name
                
                # Create ticket
                with st.spinner(f"Creating ticket in {system}..."):
                    if system == "Zammad":
                        result, error = create_zammad_ticket(client, ticket_data)
                    else:
                        result, error = create_zendesk_ticket(client, ticket_data)
                
                if error:
                    st.error(f"❌ Failed to create ticket: {error}")
                else:
                    st.success("✅ Ticket created successfully!")
                    
                    # Add to history
                    ticket_record = {
                        'system': system,
                        'title': title,
                        'customer_email': customer_email,
                        'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        'ticket_id': result.get('id') if isinstance(result, dict) else getattr(result, 'id', 'N/A')
                    }
                    st.session_state.ticket_history.append(ticket_record)
                    
                    # Show ticket details
                    st.json(result if isinstance(result, dict) else str(result))
    
    with tab2:
        st.markdown('<h2 class="section-header">Ticket History</h2>', unsafe_allow_html=True)
        
        if st.session_state.ticket_history:
            # Display tickets in a table
            import pandas as pd
            df = pd.DataFrame(st.session_state.ticket_history)
            st.dataframe(df, use_container_width=True)
            
            # Clear history button
            if st.button("🗑️ Clear History"):
                st.session_state.ticket_history = []
                st.rerun()
        else:
            st.info("📝 No tickets created yet. Create your first ticket in the 'Create Ticket' tab.")
    
    with tab3:
        st.markdown('<h2 class="section-header">Search & Manage Tickets</h2>', unsafe_allow_html=True)
        
        # Check if client is initialized
        client = st.session_state.zammad_client if system == "Zammad" else st.session_state.zendesk_client
        
        if not client:
            st.warning(f"⚠️ Please initialize the {system} client first using the sidebar.")
            return
        
        # Search functionality
        st.subheader("🔍 Search Tickets")
        col1, col2 = st.columns([2, 1])
        
        with col1:
            search_type = st.selectbox("Search by", ["Ticket ID", "Customer Email", "Title"])
            search_query = st.text_input("Search Query")
        
        with col2:
            st.write("")
            st.write("")
            search_clicked = st.button("🔍 Search", type="primary")
        
        # Initialize session state for search results
        if 'search_results' not in st.session_state:
            st.session_state.search_results = []
        if 'all_tickets' not in st.session_state:
            st.session_state.all_tickets = []
        
        # Search functionality
        if search_clicked:
            if search_query:
                with st.spinner(f"Searching {system} tickets..."):
                    if system == "Zammad":
                        results = search_zammad_tickets(client, search_type, search_query)
                    else:
                        results = search_zendesk_tickets(client, search_type, search_query)
                    
                    st.session_state.search_results = results
                    
                    if results:
                        st.success(f"✅ Found {len(results)} ticket(s)")
                    else:
                        st.info("📝 No tickets found matching your search criteria")
            else:
                st.warning("Please enter a search query")
        
        # Display search results
        if st.session_state.search_results:
            st.subheader("🎫 Search Results")
            
            # Convert tickets to display format
            display_data = []
            for ticket in st.session_state.search_results:
                display_data.append(format_ticket_for_display(ticket, system))
            
            if display_data:
                import pandas as pd
                df = pd.DataFrame(display_data)
                st.dataframe(df, use_container_width=True)
                
                # Clear search results
                if st.button("🗑️ Clear Search Results"):
                    st.session_state.search_results = []
                    st.rerun()
        
        st.divider()
        
        # Ticket management actions
        st.subheader("📋 Ticket Management")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📊 View All Tickets", type="secondary"):
                with st.spinner(f"Fetching all {system} tickets..."):
                    if system == "Zammad":
                        tickets = get_all_zammad_tickets(client)
                    else:
                        tickets = get_all_zendesk_tickets(client)
                    
                    st.session_state.all_tickets = tickets
                    
                    if tickets:
                        st.success(f"✅ Loaded {len(tickets)} ticket(s)")
                    else:
                        st.info("📝 No tickets found")
        
        with col2:
            update_clicked = st.button("✏️ Update Ticket", type="secondary")
        
        with col3:
            delete_clicked = st.button("🗑️ Delete Ticket", type="secondary")
        
        # Display all tickets
        if st.session_state.all_tickets:
            st.subheader("📊 All Tickets")
            
            # Convert tickets to display format
            display_data = []
            for ticket in st.session_state.all_tickets:
                display_data.append(format_ticket_for_display(ticket, system))
            
            if display_data:
                import pandas as pd
                df = pd.DataFrame(display_data)
                st.dataframe(df, use_container_width=True)
                
                # Clear all tickets
                if st.button("🗑️ Clear All Tickets View"):
                    st.session_state.all_tickets = []
                    st.rerun()
        
        # Update ticket functionality
        if update_clicked:
            st.subheader("✏️ Update Ticket")
            
            with st.form("update_ticket_form"):
                ticket_id = st.number_input("Ticket ID", min_value=1, step=1)
                
                if system == "Zammad":
                    update_title = st.text_input("New Title (optional)")
                    update_state = st.selectbox("New State (optional)", ["", "new", "open", "pending reminder", "pending close", "closed"])
                    update_priority = st.selectbox("New Priority (optional)", ["", "1 low", "2 normal", "3 high"])
                else:  # Zendesk
                    update_subject = st.text_input("New Subject (optional)")
                    update_status = st.selectbox("New Status (optional)", ["", "new", "open", "pending", "hold", "solved", "closed"])
                    update_priority = st.selectbox("New Priority (optional)", ["", "low", "normal", "high", "urgent"])
                
                update_submitted = st.form_submit_button("🔄 Update Ticket")
                
                if update_submitted:
                    if ticket_id:
                        # Prepare update data
                        update_data = {}
                        
                        if system == "Zammad":
                            if update_title:
                                update_data['title'] = update_title
                            if update_state:
                                update_data['state'] = update_state
                            if update_priority:
                                update_data['priority'] = update_priority
                        else:  # Zendesk
                            if update_subject:
                                update_data['subject'] = update_subject
                            if update_status:
                                update_data['status'] = update_status
                            if update_priority:
                                update_data['priority'] = update_priority
                        
                        if update_data:
                            with st.spinner(f"Updating ticket {ticket_id}..."):
                                if system == "Zammad":
                                    result, error = update_zammad_ticket(client, ticket_id, update_data)
                                else:
                                    result, error = update_zendesk_ticket(client, ticket_id, update_data)
                                
                                if error:
                                    st.error(f"❌ Failed to update ticket: {error}")
                                else:
                                    st.success(f"✅ Ticket {ticket_id} updated successfully!")
                                    st.json(result if isinstance(result, dict) else str(result))
                        else:
                            st.warning("Please provide at least one field to update")
                    else:
                        st.warning("Please enter a valid ticket ID")
        
        # Delete ticket functionality
        if delete_clicked:
            st.subheader("🗑️ Delete Ticket")
            
            st.warning("⚠️ **Warning:** This action cannot be undone!")
            
            with st.form("delete_ticket_form"):
                delete_ticket_id = st.number_input("Ticket ID to Delete", min_value=1, step=1)
                confirm_delete = st.checkbox("I confirm that I want to delete this ticket")
                
                delete_submitted = st.form_submit_button("🗑️ Delete Ticket", type="primary")
                
                if delete_submitted:
                    if delete_ticket_id and confirm_delete:
                        with st.spinner(f"Deleting ticket {delete_ticket_id}..."):
                            if system == "Zammad":
                                result, error = delete_zammad_ticket(client, delete_ticket_id)
                            else:
                                result, error = delete_zendesk_ticket(client, delete_ticket_id)
                            
                            if error:
                                st.error(f"❌ Failed to delete ticket: {error}")
                            else:
                                st.success(f"✅ Ticket {delete_ticket_id} deleted successfully!")
                                # Clear any cached results that might contain the deleted ticket
                                if 'search_results' in st.session_state:
                                    st.session_state.search_results = []
                                if 'all_tickets' in st.session_state:
                                    st.session_state.all_tickets = []
                    elif not confirm_delete:
                        st.warning("Please confirm that you want to delete the ticket")
                    else:
                        st.warning("Please enter a valid ticket ID")
    
    with tab4:
        st.markdown('<h2 class="section-header">Settings</h2>', unsafe_allow_html=True)
        
        # Environment variables configuration
        st.subheader("🔐 Environment Variables")
        
        with st.expander("Zammad Configuration"):
            zammad_url = st.text_input("ZAMMAD_URL", value=os.getenv('ZAMMAD_URL', ''))
            zammad_token = st.text_input("ZAMMAD_HTTP_TOKEN", value=os.getenv('ZAMMAD_HTTP_TOKEN', ''), type="password")
            zammad_username = st.text_input("ZAMMAD_USERNAME", value=os.getenv('ZAMMAD_USERNAME', ''))
            zammad_password = st.text_input("ZAMMAD_PASSWORD", value=os.getenv('ZAMMAD_PASSWORD', ''), type="password")
        
        with st.expander("Zendesk Configuration"):
            zendesk_email = st.text_input("ZENDESK_EMAIL", value=os.getenv('ZENDESK_EMAIL', ''))
            zendesk_token = st.text_input("ZENDESK_TOKEN", value=os.getenv('ZENDESK_TOKEN', ''), type="password")
            zendesk_subdomain = st.text_input("ZENDESK_SUBDOMAIN", value=os.getenv('ZENDESK_SUBDOMAIN', ''))
        
        with st.expander("Groq API Configuration"):
            groq_api_key = st.text_input("GROQ_API_KEY", value=os.getenv('GROQ_API_KEY', ''), type="password")
        
        # Application settings
        st.subheader("⚙️ Application Settings")
        
        # Theme selection
        theme = st.selectbox("Theme", ["Light", "Dark"], index=0)
        
        # Auto-refresh settings
        auto_refresh = st.checkbox("Auto-refresh ticket list", value=False)
        if auto_refresh:
            refresh_interval = st.slider("Refresh interval (seconds)", 10, 300, 60)
        
        # Notification settings
        st.subheader("🔔 Notifications")
        email_notifications = st.checkbox("Email notifications", value=True)
        desktop_notifications = st.checkbox("Desktop notifications", value=False)
        
        # Save settings
        if st.button("💾 Save Settings"):
            st.success("✅ Settings saved successfully!")
    
    # Footer
    st.markdown("---")
    st.markdown(
        '<div style="text-align: center; color: #666; margin-top: 2rem;">'
        '🎫 RouteIQ Ticket Management System | Built with Streamlit'
        '</div>',
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
