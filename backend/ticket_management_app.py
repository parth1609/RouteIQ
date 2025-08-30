import streamlit as st
import os
import json
import sys
from datetime import datetime
from dotenv import load_dotenv
import requests

# Add the current directory to Python path to import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import our integration modules
from zammad.zammad_api import check_classifier_health

# Load environment variables
load_dotenv()

# Backend API base for FastAPI services
API_BASE = os.getenv('ROUTEIQ_API_BASE', 'http://127.0.0.1:8000/api/v1')

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
if 'ticket_history' not in st.session_state:
    st.session_state.ticket_history = []

## Removed legacy client initialization; all operations now use FastAPI

## Removed legacy Zammad ticket creation helpers (SDK- and module-based)

def fastapi_zammad_create_ticket(ticket_data):
    """Create a ticket in Zammad using the FastAPI service"""
    try:
        # Prepare API request
        url = f"{API_BASE}/zammad/tickets"
        response = requests.post(url, json=ticket_data, timeout=20)
        if response.ok:
            return response.json(), None
        # Try to surface backend-provided detail
        try:
            return None, response.json().get("detail") or response.text
        except Exception:
            return None, response.text
    except Exception as e:
        return None, str(e)

def fastapi_zammad_health():
    """Check Zammad API health via FastAPI backend."""
    try:
        url = f"{API_BASE}/zammad/health"
        resp = requests.get(url, timeout=10)
        if resp.ok:
            return resp.json(), None
        try:
            return None, resp.json().get('detail') or resp.text
        except Exception:
            return None, resp.text
    except Exception as e:
        return None, str(e)

def fastapi_zammad_list_tickets():
    """List tickets via FastAPI backend. Uses v2 endpoint and falls back if needed."""
    try:
        url = f"{API_BASE}/zammad/tickets"
        resp = requests.get(url, timeout=20)
        if resp.ok:
            return resp.json(), None
        # Fallback to legacy get_all_tickets endpoint if exposed
        try:
            fb = requests.get(f"{API_BASE}/zammad/get_all_tickets", timeout=20)
            if fb.ok:
                return fb.json(), None
            try:
                return None, fb.json().get('detail') or fb.text
            except Exception:
                return None, fb.text
        except Exception:
            pass
        try:
            return None, resp.json().get('detail') or resp.text
        except Exception:
            return None, resp.text
    except Exception as e:
        return None, str(e)

def fastapi_zammad_get_ticket(ticket_id: int):
    """Get a single ticket by ID via FastAPI backend."""
    try:
        url = f"{API_BASE}/zammad/tickets/{ticket_id}"
        resp = requests.get(url, timeout=15)
        if resp.ok:
            return resp.json(), None
        try:
            return None, resp.json().get('detail') or resp.text
        except Exception:
            return None, resp.text
    except Exception as e:
        return None, str(e)

def fastapi_zammad_update_ticket(ticket_id: int, update_data: dict):
    """Update ticket via FastAPI backend."""
    try:
        url = f"{API_BASE}/zammad/tickets/{ticket_id}"
        resp = requests.patch(url, json=update_data, timeout=20)
        if resp.ok:
            return resp.json(), None
        try:
            return None, resp.json().get('detail') or resp.text
        except Exception:
            return None, resp.text
    except Exception as e:
        return None, str(e)

def fastapi_zammad_delete_ticket(ticket_id: int):
    """Delete/close ticket via FastAPI backend."""
    try:
        url = f"{API_BASE}/zammad/tickets/{ticket_id}"
        resp = requests.delete(url, timeout=20)
        if resp.ok:
            return resp.json() if resp.text else {"success": True}, None
        try:
            return None, resp.json().get('detail') or resp.text
        except Exception:
            return None, resp.text
    except Exception as e:
        return None, str(e)

def fastapi_zendesk_health():
    """Check Zendesk API health via FastAPI backend."""
    try:
        url = f"{API_BASE}/zendesk/health"
        resp = requests.get(url, timeout=10)
        if resp.ok:
            return resp.json(), None
        try:
            return None, resp.json().get('detail') or resp.text
        except Exception:
            return None, resp.text
    except Exception as e:
        return None, str(e)

def fastapi_zendesk_create_ticket(ticket_data: dict):
    """Create a ticket in Zendesk via FastAPI backend."""
    try:
        url = f"{API_BASE}/zendesk/tickets"
        resp = requests.post(url, json=ticket_data, timeout=20)
        if resp.ok:
            return resp.json(), None
        try:
            return None, resp.json().get('detail') or resp.text
        except Exception:
            return None, resp.text
    except Exception as e:
        return None, str(e)

## Removed legacy Zendesk client-based creation helper

def search_zammad_tickets(client, search_type, search_query):
    """Search tickets in Zammad via FastAPI.
    For Ticket ID, calls the ticket GET endpoint. For other searches, lists tickets and filters client-side.
    """
    try:
        if search_type == "Ticket ID":
            data, err = fastapi_zammad_get_ticket(int(search_query))
            if err:
                st.error(f"Error fetching ticket: {err}")
                return []
            return [data] if data else []
        else:
            tickets, err = fastapi_zammad_list_tickets()
            if err:
                st.error(f"Error listing tickets: {err}")
                return []
            if not tickets:
                return []
            # Normalize to list
            if isinstance(tickets, dict) and 'tickets' in tickets:
                tickets = tickets['tickets']
            results = []
            q = str(search_query).lower()
            for t in tickets:
                try:
                    if search_type == "Customer Email":
                        # Try common shapes
                        email = (
                            (t.get('customer_email')) if isinstance(t, dict) else None
                        )
                        if not email and isinstance(t, dict) and isinstance(t.get('customer'), dict):
                            email = t['customer'].get('email')
                        if email and q in str(email).lower():
                            results.append(t)
                    elif search_type == "Title":
                        title = t.get('title') if isinstance(t, dict) else None
                        if title and q in str(title).lower():
                            results.append(t)
                except Exception:
                    continue
            return results
    except Exception as e:
        st.error(f"Error searching Zammad tickets: {str(e)}")
        return []

## Removed legacy Zendesk search helper (no FastAPI endpoints yet)

def get_all_zammad_tickets(client, limit=50):
    """Get all tickets from Zammad via FastAPI."""
    try:
        tickets, err = fastapi_zammad_list_tickets()
        if err:
            st.error(f"Error fetching Zammad tickets: {err}")
            return []
        if not tickets:
            return []
        if isinstance(tickets, dict) and 'tickets' in tickets:
            tickets = tickets['tickets']
        # Limit results
        return list(tickets)[:limit]
    except Exception as e:
        st.error(f"Error fetching Zammad tickets: {str(e)}")
        return []

## Removed legacy Zendesk list helper (no FastAPI endpoints yet)

def update_zammad_ticket(client, ticket_id, update_data):
    """Update a ticket in Zammad via FastAPI."""
    try:
        result, err = fastapi_zammad_update_ticket(ticket_id, update_data)
        if err:
            return None, err
        return result, None
    except Exception as e:
        return None, str(e)

## Removed legacy Zendesk update helper (no FastAPI endpoints yet)

def delete_zammad_ticket(client, ticket_id):
    """Delete/close a ticket in Zammad via FastAPI."""
    try:
        result, err = fastapi_zammad_delete_ticket(ticket_id)
        if err:
            return None, err
        return result, None
    except Exception as e:
        return None, f"Error deleting ticket: {str(e)}"

## Removed legacy Zendesk delete helper (no FastAPI endpoints yet)

def resolve_zammad_ids(client, ticket):
    """Resolve Zammad ticket IDs to actual names"""
    resolved_data = {}
    
    try:
        # Resolve state
        if 'state_id' in ticket and ticket['state_id']:
            try:
                state = client.ticket_state.find(ticket['state_id'])
                resolved_data['state'] = state.get('name', f"State ID: {ticket['state_id']}")
            except:
                resolved_data['state'] = f"State ID: {ticket['state_id']}"
        
        # Resolve priority
        if 'priority_id' in ticket and ticket['priority_id']:
            try:
                priority = client.ticket_priority.find(ticket['priority_id'])
                resolved_data['priority'] = priority.get('name', f"Priority ID: {ticket['priority_id']}")
            except:
                resolved_data['priority'] = f"Priority ID: {ticket['priority_id']}"
        
        # Resolve customer
        if 'customer_id' in ticket and ticket['customer_id']:
            try:
                customer = client.user.find(ticket['customer_id'])
                if customer:
                    name_parts = []
                    if customer.get('firstname'):
                        name_parts.append(customer['firstname'])
                    if customer.get('lastname'):
                        name_parts.append(customer['lastname'])
                    if customer.get('email'):
                        name_parts.append(f"({customer['email']})")
                    resolved_data['customer'] = ' '.join(name_parts) if name_parts else f"Customer ID: {ticket['customer_id']}"
                else:
                    resolved_data['customer'] = f"Customer ID: {ticket['customer_id']}"
            except:
                resolved_data['customer'] = f"Customer ID: {ticket['customer_id']}"
        
        # Resolve group
        if 'group_id' in ticket and ticket['group_id']:
            try:
                group = client.group.find(ticket['group_id'])
                resolved_data['group'] = group.get('name', f"Group ID: {ticket['group_id']}")
            except:
                resolved_data['group'] = f"Group ID: {ticket['group_id']}"
                
    except Exception as e:
        # If there's any error, just return empty dict and fall back to IDs
        pass
    
    return resolved_data

def format_ticket_for_display(ticket, system, client=None):
    """Format ticket data for display in Streamlit"""
    if system == "Zammad":
        def safe_get(obj, key, default='N/A'):
            if isinstance(obj, dict):
                value = obj.get(key, default)
                return str(value) if value is not None and value != default else default
            elif hasattr(obj, key):
                value = getattr(obj, key, default)
                return str(value) if value is not None and value != default else default
            else:
                return default
        
        # Try to resolve IDs to names if client is provided
        resolved_data = {}
        if client:
            resolved_data = resolve_zammad_ids(client, ticket)
        
        # Use resolved data or fall back to IDs
        state_value = resolved_data.get('state', f"State ID: {safe_get(ticket, 'state_id')}")
        priority_value = resolved_data.get('priority', f"Priority ID: {safe_get(ticket, 'priority_id')}")
        customer_value = resolved_data.get('customer', f"Customer ID: {safe_get(ticket, 'customer_id')}")
        group_value = resolved_data.get('group', f"Group ID: {safe_get(ticket, 'group_id')}")
        
        return {
            "ID": safe_get(ticket, 'id'),
            "Title": safe_get(ticket, 'title'),
            "State": state_value,
            "Priority": priority_value,
            "Customer": customer_value,
            "Group": group_value,
            "Created": safe_get(ticket, 'created_at'),
            "Updated": safe_get(ticket, 'updated_at')
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
    
    # Service health (FastAPI-backed)
    # Classifier health
    try:
        health_status = check_classifier_health()
        if health_status.get("status") == "healthy":
            st.success(f"✅ Classifier: Online (v{health_status.get('version', 'unknown')})")
        else:
            st.warning("⚠️ Classifier: Offline")
    except Exception:
        st.warning("⚠️ Classifier: Unavailable")
    
    # Zammad API health
    try:
        z_health, z_err = fastapi_zammad_health()
        if z_err:
            st.warning(f"⚠️ Zammad API: {z_err}")
        else:
            status = z_health.get('status') or z_health.get('message') or 'unknown'
            if str(status).lower() in ("ok", "healthy", "online"):
                st.success("✅ Zammad API: Online")
            else:
                st.warning(f"⚠️ Zammad API: {status}")
    except Exception:
        st.warning("⚠️ Zammad API: Unavailable")
    
    # Zendesk API health
    try:
        zd_health, zd_err = fastapi_zendesk_health()
        if zd_err:
            st.warning(f"⚠️ Zendesk API: {zd_err}")
        else:
            status = zd_health.get('status') or zd_health.get('message') or 'unknown'
            if str(status).lower() in ("ok", "healthy", "online"):
                st.success("✅ Zendesk API: Online")
            else:
                st.warning(f"⚠️ Zendesk API: {status}")
    except Exception:
        st.warning("⚠️ Zendesk API: Unavailable")
    
    # Environment variables check
    st.subheader("🔐 Environment Variables")
    env_vars = {
        "Zammad": ["ZAMMAD_URL", "ZAMMAD_HTTP_TOKEN"],
        "Zendesk": ["ZENDESK_EMAIL", "ZENDESK_TOKEN", "ZENDESK_SUBDOMAIN"]
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
    
    # No client initialization required; FastAPI is used for all operations
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
                # Static options; actual routing/creation handled by FastAPI backend
                group_options = ["Auto (Use AI)", "Users"]
                group = st.selectbox("Group/Department", group_options)
                
                # Step 1: Show instructions before classification and naming convention guidance
                st.info("Please create the dept/group what they want and if dept/group is already there, give all the permissions as an admin/agent.")
                st.caption("Naming convention for new groups — Correct: 'Customer Service'; Incorrect: 'Dept - Customer Service'.")
                # Ask for permission to create a new group only if it's missing
                create_if_missing = st.checkbox(
                    "Allow creating new department/group if missing",
                    value=False,
                    help="When enabled, the app will create the predicted department/group in Zammad if it does not exist."
                )
            
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
                # include permission creation preference for missing groups
                ticket_data['create_if_missing'] = create_if_missing
            elif system == "Zendesk":
                ticket_data['assignee_email'] = assignee_email
                ticket_data['assignee_name'] = assignee_name
            
            # Create ticket
            with st.spinner(f"Creating ticket in {system}..."):
                if system == "Zammad":
                    result, error = fastapi_zammad_create_ticket(ticket_data)
                else:
                    result, error = fastapi_zendesk_create_ticket(ticket_data)
            
            if error:
                st.error(f"❌ Failed to create ticket: {error}")
            else:
                st.success("✅ Ticket created successfully!")
                
                # If using auto-group, surface instructions/warnings
                if system == "Zammad" and isinstance(result, dict):
                    assigned_group = result.get("assigned_group") or result.get("group")
                    created_group_name = result.get("created_group_name")
                    if assigned_group:
                        st.info(f"🏷️ Assigned Group: {assigned_group}")
                    if result.get("new_group_created"):
                        st.info("🔔 A new department/group was created automatically.")
                        # Display admin permission instructions
                        group_to_grant = created_group_name or assigned_group or "<new group>"
                        st.warning(
                            "\n".join([
                                "ACTION REQUIRED: Grant permissions for the new department/group",
                                "1. Go to Admin > Roles",
                                "2. Edit the appropriate role for the API user",
                                f"3. Under 'Group Permissions', set '{group_to_grant}' to 'Full'",
                                "4. Save changes",
                                "Once granted, future tickets will be created directly in this group without fallback."
                            ])
                        )
                    if result.get("permission_warning") or result.get("fallback_group_used"):
                        fallback_group = result.get("fallback_group")
                        warn_txt = "Permissions missing for the intended group. "
                        if fallback_group:
                            warn_txt += f"Ticket was created in fallback group '{fallback_group}'."
                        st.warning(warn_txt)
                        # Provide admin steps even when we fell back (not only when a group was newly created)
                        group_to_grant = result.get("created_group_name") or result.get("assigned_group") or result.get("resolved_group") or result.get("group") or "<group>"
                        st.info(
                            "\n".join([
                                "ACTION REQUIRED: Grant permissions for the intended department/group",
                                "1. Go to Admin > Roles",
                                "2. Edit the appropriate role for the API user",
                                f"3. Under 'Group Permissions', set '{group_to_grant}' to 'Full'",
                                "4. Save changes",
                                "Once granted, future tickets will be created directly in this group without fallback."
                            ])
                        )
                
                # Add to history
                ticket_record = {
                    'system': system,
                    'title': title,
                    'customer_email': customer_email,
                    'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'ticket_id': result.get('ticket_id') if isinstance(result, dict) else getattr(result, 'id', 'N/A')
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
    
    # FastAPI-only: no SDK clients required
    client = None
    
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
                    st.info("Zendesk search will be available once FastAPI endpoints are added (get/list/search).")
                    results = []
                
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
            display_data.append(format_ticket_for_display(ticket, system, client))
        
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
    
    # Initialize session state for UI management
    if 'show_update_form' not in st.session_state:
        st.session_state.show_update_form = False
    if 'show_delete_form' not in st.session_state:
        st.session_state.show_delete_form = False
    
    with col1:
        if st.button("📊 View All Tickets", type="secondary"):
            with st.spinner(f"Fetching all {system} tickets..."):
                if system == "Zammad":
                    tickets = get_all_zammad_tickets(client)
                else:
                    st.info("Zendesk list will be available once FastAPI endpoints are added (list).")
                    tickets = []
                
                st.session_state.all_tickets = tickets
                
                if tickets:
                    st.success(f"✅ Loaded {len(tickets)} ticket(s)")
                else:
                    st.info("📝 No tickets found")
    
    with col2:
        if st.button("✏️ Update Ticket", type="secondary"):
            st.session_state.show_update_form = not st.session_state.show_update_form
            st.session_state.show_delete_form = False  # Hide delete form
    
    with col3:
        if st.button("🗑️ Delete Ticket", type="secondary"):
            st.session_state.show_delete_form = not st.session_state.show_delete_form
            st.session_state.show_update_form = False  # Hide update form
    
    # Display all tickets
    if st.session_state.all_tickets:
        st.subheader("📊 All Tickets")
        
        # Convert tickets to display format
        display_data = []
        for ticket in st.session_state.all_tickets:
            display_data.append(format_ticket_for_display(ticket, system, client))
        
        if display_data:
            import pandas as pd
            df = pd.DataFrame(display_data)
            st.dataframe(df, use_container_width=True)
            
            # Clear all tickets
            if st.button("🗑️ Clear All Tickets View"):
                st.session_state.all_tickets = []
                st.rerun()
    
    # Update ticket functionality
    if st.session_state.show_update_form:
        st.divider()
        st.subheader("✏️ Update Ticket")
        
        with st.form("update_ticket_form"):
            ticket_id = st.number_input("Ticket ID", min_value=1, step=1, key="update_ticket_id")
            
            if system == "Zammad":
                update_title = st.text_input("New Title (optional)", key="update_title")
                update_state = st.selectbox("New State (optional)", ["", "new", "open", "pending reminder", "pending close", "closed"], key="update_state")
                update_priority = st.selectbox("New Priority (optional)", ["", "1 low", "2 normal", "3 high"], key="update_priority")
            else:  # Zendesk
                update_subject = st.text_input("New Subject (optional)", key="update_subject")
                update_status = st.selectbox("New Status (optional)", ["", "new", "open", "pending", "hold", "solved", "closed"], key="update_status")
                update_priority = st.selectbox("New Priority (optional)", ["", "low", "normal", "high", "urgent"], key="update_priority_zd")
            
            col1, col2 = st.columns([1, 1])
            with col1:
                update_submitted = st.form_submit_button("🔄 Update Ticket", type="primary")
            with col2:
                cancel_update = st.form_submit_button("❌ Cancel")
            
            if cancel_update:
                st.session_state.show_update_form = False
                st.rerun()
            
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
                                st.info("Zendesk update will be available once FastAPI endpoints are added (update).")
                                result, error = None, None
                            
                            if error:
                                st.error(f"❌ Failed to update ticket: {error}")
                            else:
                                st.success(f"✅ Ticket {ticket_id} updated successfully!")
                                if isinstance(result, dict):
                                    st.json(result)
                                else:
                                    st.write(f"Result: {str(result)}")
                                # Hide form after successful update
                                st.session_state.show_update_form = False
                    else:
                        st.warning("Please provide at least one field to update")
                else:
                    st.warning("Please enter a valid ticket ID")
    
    # Delete ticket functionality
    if st.session_state.show_delete_form:
        st.divider()
        st.subheader("🗑️ Delete Ticket")
        
        st.warning("⚠️ **Warning:** This action cannot be undone!")
        
        if system == "Zammad":
            st.info("📝 **Note:** Zammad tickets will be closed instead of permanently deleted.")
        elif system == "Zendesk":
            st.info("📝 **Note:** Zendesk tickets will be closed and marked as deleted (soft delete).")
        
        with st.form("delete_ticket_form"):
            delete_ticket_id = st.number_input("Ticket ID to Delete", min_value=1, step=1, key="delete_ticket_id")
            confirm_delete = st.checkbox("I confirm that I want to delete this ticket", key="confirm_delete")
            
            col1, col2 = st.columns([1, 1])
            with col1:
                delete_submitted = st.form_submit_button("🗑️ Delete Ticket", type="primary")
            with col2:
                cancel_delete = st.form_submit_button("❌ Cancel")
            
            if cancel_delete:
                st.session_state.show_delete_form = False
                st.rerun()
            
            if delete_submitted:
                if delete_ticket_id and confirm_delete:
                    with st.spinner(f"Deleting ticket {delete_ticket_id}..."):
                        if system == "Zammad":
                            result, error = delete_zammad_ticket(client, delete_ticket_id)
                        else:
                            st.info("Zendesk delete will be available once FastAPI endpoints are added (delete/close).")
                            result, error = None, None
                        
                        if error:
                            st.error(f"❌ Failed to delete ticket: {error}")
                        else:
                            st.success(f"✅ Ticket {delete_ticket_id} deleted successfully!")
                            # Clear any cached results that might contain the deleted ticket
                            if 'search_results' in st.session_state:
                                st.session_state.search_results = []
                            if 'all_tickets' in st.session_state:
                                st.session_state.all_tickets = []
                            # Hide form after successful deletion
                            st.session_state.show_delete_form = False
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
    
    # FastAPI Classifier Configuration section removed
    
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

# from root dir
#  cd backend && streamlit run ticket_management_app.py