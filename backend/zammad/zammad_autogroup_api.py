import os
import sys
import requests
import traceback
from typing import Dict, Any, Optional, Union
from dotenv import load_dotenv

# Ensure local imports work when run directly
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(CURRENT_DIR)
if PARENT_DIR not in sys.path:
    sys.path.append(PARENT_DIR)

load_dotenv()

# Reuse models from existing zammad_api without modifying it
from zammad.zammad_integration import initialize_zammad_client, get_all_groups, find_or_create_customer
from zammad.group_tools import ensure_group
from zammad import zammad_api as base_api  # import existing models

# Classifier URL configurable here independently of zammad_api
API_URL = os.getenv("CLASSIFIER_API_URL", "http://127.0.0.1:8000/api/v1/")
PREDICT_URL = f"{API_URL}predict"
HEALTH_URL = f"{API_URL}health"

# Type aliases from base_api for clarity
Ticket = base_api.Ticket
Customer = base_api.Customer
TicketPriority = base_api.TicketPriority
TicketClassifierResponse = base_api.TicketClassifierResponse


def check_classifier_health() -> Dict[str, Any]:
    try:
        r = requests.get(HEALTH_URL, timeout=10)
        r.raise_for_status()
        return r.json()
    except requests.RequestException as e:
        return {"status": "error", "message": str(e)}


def predict_ticket_category(description: str) -> Dict[str, Any]:
    """
    Call classifier and ALWAYS return a normalized dict:
      { success: bool, department: str, priority: str, error?: str }
    This avoids attribute errors when callers use .get().
    """
    try:
        r = requests.post(PREDICT_URL, json={"description": description}, timeout=20)
        r.raise_for_status()
        data = r.json()

        # Normalize common formats
        if isinstance(data, dict):
            if "department" in data and "priority" in data:
                return {"success": True, "department": data["department"], "priority": data["priority"]}
            if "prediction" in data and isinstance(data["prediction"], dict):
                pred = data["prediction"]
                return {
                    "success": True,
                    "department": pred.get("department", "General"),
                    "priority": pred.get("priority", "Normal"),
                }

        return {
            "success": False,
            "department": "General",
            "priority": "Normal",
            "error": f"Unexpected classifier response format: {data}",
        }
    except requests.RequestException as e:
        return {
            "success": False,
            "department": "General",
            "priority": "Normal",
            "error": f"Classifier request failed: {str(e)}",
        }


def create_prefixed_group(client, base_name: str, prefix: str = "Users - ") -> Dict[str, Any]:
    """Create a group with a prefixed name (e.g., 'Users - IT Support')"""
    prefixed_name = f"{prefix}{base_name}"
    return ensure_group(client=client, name=prefixed_name)

def notify_admin(client, message: str, ticket_id: int = None) -> None:
    """Send a notification to admin users about a new department that needs permissions"""
    try:
        admin_users = client.user.search("role_ids:1")  # Role ID 1 is typically Admin
        if not admin_users:
            print("Warning: No admin users found to notify")
            return

        subject = "New Department Created - Permission Review Needed"
        body = f"""
        A new department was automatically created for a ticket, but permissions need to be configured.

        {message}

        Please review and assign appropriate permissions in Zammad Admin > Roles.
        """
        
        if ticket_id:
            ticket_url = f"{os.getenv('ZAMMAD_URL')}/#ticket/zoom/{ticket_id}"
            body += f"\n\nTicket: {ticket_url}"

        for admin in admin_users:
            try:
                client.user_preferences.notification_send(
                    admin['id'],
                    subject=subject,
                    body=body,
                    content_type='text/plain',
                )
            except Exception as e:
                print(f"Failed to notify admin {admin.get('email')}: {str(e)}")
        
        print(f"Notification sent to {len(admin_users)} admin(s)")
    except Exception as e:
        print(f"Failed to send admin notification: {str(e)}")

def create_ticket_with_autogroup(ticket: Ticket, prefix: str = "") -> Dict[str, Any]:
    """
    Create a Zammad ticket using auto group resolution/creation.
    If a predicted department doesn't exist, creates it and notifies admins.
    """
    try:
        print("\n🔌 Initializing Zammad client...")
        client = initialize_zammad_client()
        
        print("📋 Fetching all groups...")
        groups = get_all_groups(client)
        print(f"   Found {len(groups)} groups: {', '.join(groups.keys())}")
        
        print("\n👤 Processing customer...")
        customer_id = find_or_create_customer(
            client,
            ticket.customer.email,
            ticket.customer.firstname,
            ticket.customer.lastname,
        )
        if not customer_id:
            return {"success": False, "error": "Failed to find or create customer"}
        print(f"   Customer ID: {customer_id}")

        resolved_group_name = None
        new_group_created = False

        # 1) Use explicit group if provided
        if ticket.group_name:
            print(f"\n🎯 Using explicit group: {ticket.group_name}")
            group_name = ticket.group_name.strip()
            if group_name not in groups:
                print(f"   Group '{group_name}' not found, creating new group...")
                created = create_prefixed_group(client, group_name, prefix)
                if created:
                    groups[created['name']] = created['id']
                    new_group_created = True
                    print(f"✅ Created new group: {created['name']} (ID: {created['id']})")
                    notify_admin(
                        client,
                        f"New group created: {created['name']} (ID: {created['id']})\n\n"
                        f"This group was created for ticket with subject: {ticket.title}",
                        ticket_id=created.get('id')
                    )
                    print("📬 Sent notification to admin about new group")
            group_id = groups.get(group_name)
            resolved_group_name = group_name
            print(f"   Using group ID: {group_id}")
        else:
            # 2) Predict department using classifier
            print("\n🤖 Predicting department using classifier...")
            classification = predict_ticket_category(ticket.description)
            print(f"   Raw classification: {classification}")
            
            # Extract department from classification
            dept = classification.get('department', 'General')
            priority = classification.get('priority', 'Normal')
            
            if not classification.get('success', False):
                print(f"⚠️  {classification.get('error', 'Classification failed')}")
                print(f"   Using fallback department: {dept}, priority: {priority}")
            else:
                print(f"✅ Predicted department: {dept}, priority: {priority}")
            
            # Add prefix to department name if needed
            dept_name = f"{prefix}{dept}" if not dept.startswith(prefix) else dept
            print(f"   Formatted department name: {dept_name}")
            resolved_group_name = dept_name
            
            # Update ticket priority if available (TicketPriority is a Pydantic model, not Enum)
            if priority and hasattr(ticket, 'priority'):
                try:
                    pr_map = {"LOW": "low", "NORMAL": "normal", "HIGH": "high"}
                    normalized = pr_map.get(str(priority).upper(), "normal")
                    # If ticket.priority is already a TicketPriority instance, update its field
                    if isinstance(ticket.priority, TicketPriority):
                        ticket.priority.priority = normalized
                    else:
                        ticket.priority = TicketPriority(priority=normalized)
                    print(f"   Set ticket priority to: {normalized}")
                except Exception:
                    print(f"⚠️  Invalid priority '{priority}', using default")
            
            # Create group if it doesn't exist
            if dept_name not in groups:
                print(f"   Group '{dept_name}' not found, creating new group...")
                created = create_prefixed_group(client, dept, prefix)
                if created:
                    groups[created['name']] = created['id']
                    new_group_created = True
                    print(f"✅ Created new group: {created['name']} (ID: {created['id']})")
                    notify_admin(
                        client,
                        f"New department group created: {created['name']} (ID: {created['id']})\n\n"
                        f"Predicted from ticket subject: {ticket.title}\n"
                        f"Please assign appropriate permissions in Admin > Roles.",
                        ticket_id=created.get('id')
                    )
                    print("📬 Sent notification to admin about new department")
            else:
                print(f"   Using existing group: {dept_name} (ID: {groups[dept_name]})")
                
            group_id = groups.get(dept_name)

        # 3) Fallback to first available group if needed
        if not group_id:
            if groups:
                group_name, group_id = next(iter(groups.items()))
                warning = f"⚠️  No valid group found, using fallback: {group_name} (ID: {group_id})"
                print(warning)
                return {
                    "success": False,
                    "error": "No valid group available",
                    "warning": warning,
                    "resolved_group": resolved_group_name,
                    "new_group_created": new_group_created,
                }
            else:
                error = "❌ No groups available in Zammad"
                print(error)
                return {"success": False, "error": error}

        # Create ticket with the resolved group_id
        print(f"\n🎫 Creating ticket in group ID {group_id}...")
        params = ticket.to_zammad_params(customer_id, group_id)
        print(f"   Zammad params: {params}")
        
        try:
            created_ticket = client.ticket.create(params=params)
            print(f"✅ Successfully created ticket #{created_ticket.get('id')}")
            return {
                "success": True, 
                "ticket": created_ticket,
                "resolved_group": resolved_group_name,
                "new_group_created": new_group_created,
                "warning": ("New group created, please assign permissions" if new_group_created else None),
            }
        except Exception as e:
            error_msg = str(e)
            print(f"❌ Error creating ticket: {error_msg}")
            
            if "Not authorized" in error_msg and len(groups) > 1:
                fallback_name, fallback_id = next(iter(groups.items()))
                print(f"⚠️  Permission denied. Trying fallback group: {fallback_name} (ID: {fallback_id})")
                
                try:
                    params = ticket.to_zammad_params(customer_id, fallback_id)
                    created_ticket = client.ticket.create(params=params)
                    print(f"✅ Successfully created ticket in fallback group: {fallback_name}")
                    return {
                        "success": True,
                        "ticket": created_ticket,
                        "resolved_group": resolved_group_name,
                        "new_group_created": new_group_created,
                        "warning": f"Used fallback group '{fallback_name}' due to permission error"
                    }
                except Exception as fallback_error:
                    print(f"❌ Fallback group also failed: {str(fallback_error)}")
                    return {
                        "success": False,
                        "error": f"Failed to create ticket in any group. Last error: {str(fallback_error)}",
                        "original_error": error_msg,
                        "resolved_group": resolved_group_name,
                        "new_group_created": new_group_created,
                    }
            
            # If we get here, re-raise the original error
            raise
    except Exception as e:
        return {"success": False, "error": str(e), "trace": traceback.format_exc()}


def print_permission_instructions(group_name: str, ticket_id: int) -> None:
    print("\n🔔 ACTION REQUIRED: Grant permissions for the new department/group")
    print(f"1. Go to Admin > Roles")
    print(f"2. Edit the appropriate role")
    print(f"3. Under 'Group Permissions', set '{group_name}' to 'Full'")
    print(f"4. Save changes")
    print(f"Once an admin grants 'Full' permissions for this group to the API user's role, future tickets will be created directly in this group without fallback.")


if __name__ == "__main__":
    # Minimal manual test runner; rely on environment variables and hardcoded sample
    import argparse

    parser = argparse.ArgumentParser(description="Create Zammad ticket with auto group handling (experimental)")
    parser.add_argument("--email", default="test@example.com", help="Customer email address")
    parser.add_argument("--first", default="Test", help="Customer first name")
    parser.add_argument("--last", default="User", help="Customer last name")
    parser.add_argument("--title", default="Printer not working", help="Ticket subject/title")
    parser.add_argument("--desc", default="The office printer shows a paper jam error and won't print.", 
                       help="Ticket description (used for department prediction)")
    parser.add_argument("--group", default=None, help="Explicit group/department name to use (optional)")
    parser.add_argument("--prefix", default="", 
                       help="Prefix for auto-created groups (default: '')")
    args = parser.parse_args()

    print(f"Creating ticket with subject: {args.title}")
    if args.group:
        print(f"Using explicit group: {args.group}")
    else:
        print("No group specified, will predict department from description")
    
    print("-" * 50)
    
    t = Ticket(
        title=args.title,
        description=args.desc,
        customer=Customer(email=args.email, firstname=args.first, lastname=args.last),
        group_name=args.group,
    )
    
    result = create_ticket_with_autogroup(t, prefix=args.prefix)
    
    print("\n" + "=" * 50)
    if result.get('success'):
        ticket = result['ticket']
        ticket_id = ticket.get('id')
        group_id = ticket.get('group_id')
        
        # Get group name from return or fetch from API
        resolved_group_name = result.get('resolved_group')
        if not resolved_group_name:
            client = initialize_zammad_client()
            groups = get_all_groups(client)
            resolved_group_name = next((name for name, gid in groups.items() if gid == group_id), f"ID {group_id}")
        
        print(f"\n🎫 Ticket #{ticket_id} created successfully!")
        print(f"📌 Assigned to: {resolved_group_name} (ID: {group_id})")
        
        # Show warning if there was a fallback
        if result.get('warning'):
            print(f"\n⚠️  Note: {result['warning']}")
        # If a new group was created or we fell back due to permissions, give clear admin instructions
        if result.get('new_group_created') or ('permission' in str(result.get('warning', '')).lower()):
            print_permission_instructions(resolved_group_name, ticket_id)
    else:
        print(f"❌ Failed to create ticket: {result.get('error', 'Unknown error')}")
        if result.get('trace'):
            print(result['trace'])