import os
import json
import requests
from dotenv import load_dotenv, find_dotenv

from zammad_py import ZammadAPI
from typing import Dict

# Load environment variables from project root .env regardless of current working directory
load_dotenv(find_dotenv(usecwd=True), override=True)

def initialize_zammad_client():
    """
    Initialize and return a Zammad API client with proper error handling.
    """
    ZAMMAD_URL = os.getenv('ZAMMAD_URL')
    if not ZAMMAD_URL:
        raise ValueError("ZAMMAD_URL environment variable is not set")

    ZAMMAD_HTTP_TOKEN = os.getenv('ZAMMAD_HTTP_TOKEN')
    ZAMMAD_USERNAME = os.getenv('ZAMMAD_USERNAME')
    ZAMMAD_PASSWORD = os.getenv('ZAMMAD_PASSWORD')

    client = None
    try:
        print(f"[Zammad] Using base URL: {ZAMMAD_URL}")
        if ZAMMAD_HTTP_TOKEN:
            client = ZammadAPI(url=ZAMMAD_URL, http_token=ZAMMAD_HTTP_TOKEN)
        elif ZAMMAD_USERNAME and ZAMMAD_PASSWORD:
            client = ZammadAPI(url=ZAMMAD_URL, username=ZAMMAD_USERNAME, password=ZAMMAD_PASSWORD)
        else:
            raise ValueError("Zammad credentials not found. Set either ZAMMAD_HTTP_TOKEN or both ZAMMAD_USERNAME and ZAMMAD_PASSWORD")

        # Test connection
        current_user = client.user.me()
        # Some instances may not return 'email'; accept if we have at least an id
        if not current_user or not isinstance(current_user, dict) or not current_user.get('id'):
            raise ValueError("Failed to authenticate with Zammad: Invalid response from server")

        ident = current_user.get('email') or current_user.get('login') or current_user.get('id')
        print(f"Successfully connected to Zammad as: {ident}")
        return client

    except Exception as e:
        raise RuntimeError(f"Failed to initialize Zammad client: {str(e)}")

# Note: Do not initialize a global client at import time.
# This module is also used by a FastAPI app; failing here would crash the server.
client = None  # For backwards compatibility in scripts; initialized in main()


def get_all_groups(client_obj) -> Dict[str, int]:
    """
    Retrieves all Zammad groups and returns a dictionary mapping group names to IDs.
    Falls back gracefully if any error occurs.
    """
    groups_map: Dict[str, int] = {}
    print("\n--- Fetching Zammad Groups (Departments) ---")
    try:
        groups = list(client_obj.group.all())  # Most Zammad client versions expect no args
        if not groups:
            print("No groups found in your Zammad instance.")
        else:
            for group in groups:
                group_id = group.get("id")
                group_name = group.get("name")
                if group_id and group_name:
                    groups_map[group_name] = group_id
                    print(f"  ID: {group_id}, Name: {group_name}")
    except Exception as e:
        print(f"Warning: Unable to fetch groups: {e}")
    print("---------------------------------------------")
    return groups_map


def _ticket_to_dict(ticket: dict) -> dict:
    """Serialize a Zammad ticket dict into a JSON-safe minimal representation."""
    try:
        return {
            "id": ticket.get("id"),
            "number": ticket.get("number"),
            "title": ticket.get("title"),
            "state_id": ticket.get("state_id"),
            "priority_id": ticket.get("priority_id"),
            "group_id": ticket.get("group_id"),
            "customer_id": ticket.get("customer_id"),
            "created_at": ticket.get("created_at"),
            "updated_at": ticket.get("updated_at"),
        }
    except Exception as e:
        return {"error": f"failed to serialize ticket: {e}"}


def list_tickets(client_obj, state_id: int | None = None, limit: int = 50) -> list[dict]:
    """Return a list of tickets from Zammad as dicts. Optional filter by state_id and limit results."""
    try:
        items: list[dict] = []
        # Most zammad-py versions support .ticket.all(); .ticket.search could be used for filtering
        tickets = list(client_obj.ticket.all())
        for t in tickets:
            if state_id is not None and t.get("state_id") != state_id:
                continue
            items.append(_ticket_to_dict(t))
            if len(items) >= max(1, int(limit)):
                break
        return items
    except Exception as e:
        raise RuntimeError(f"Failed to list Zammad tickets: {e}")

def _safe_get_states(client_obj) -> list[dict]:
    """Best-effort retrieval of ticket states as list of dicts."""
    try:
        # Common in zammad_py
        return list(client_obj.ticket_state.all())
    except Exception:
        pass
    try:
        # Some variants expose `state`
        return list(client_obj.state.all())
    except Exception:
        return []

def find_state_id_by_name(client_obj, name: str) -> int | None:
    """
    Find a ticket state_id by its human name (case-insensitive). Returns None if not found.
    """
    try:
        target = (name or "").strip().lower()
        for st in _safe_get_states(client_obj):
            n = (st.get("name") or "").lower()
            if n == target:
                return st.get("id")
        return None
    except Exception:
        return None

def find_closed_state_id(client_obj) -> int:
    """
    Return the state_id for the "closed" state. Falls back to 4 if not found.
    This implements the memory note to use state_id, discovering it dynamically.
    """
    sid = find_state_id_by_name(client_obj, "closed")
    return sid if isinstance(sid, int) and sid > 0 else 4

def get_ticket(client_obj, ticket_id: int) -> dict:
    """Fetch a single ticket by id and serialize to a minimal dict."""
    try:
        # Prefer documented zammad-py method first
        t = None
        try:
            t = client_obj.ticket.find(ticket_id)
        except Exception:
            t = None
        # Try a few additional access patterns for compatibility with older clients
        if not t:
            try:
                t = client_obj.ticket.show(id=ticket_id)
            except Exception:
                t = None
        if not t:
            try:
                t = client_obj.ticket.get(ticket_id)
            except Exception:
                t = None
        if not t:
            try:
                t = client_obj.ticket.show(ticket_id)
            except Exception:
                t = None
        if not t:
            raise RuntimeError("Ticket not found")
        return _ticket_to_dict(t)
    except Exception as e:
        raise RuntimeError(f"Failed to get ticket {ticket_id}: {e}")

def update_ticket(client_obj, ticket_id: int, updates: dict) -> dict:
    """
    Update a ticket with robust fallbacks across SDK variants and raw HTTP.

    Purpose:
      Ensure field mutations (notably `title`) are reliably applied even when
      different zammad_py versions expect different update signatures.

    Parameters:
      - client_obj: Zammad API client instance returned by `initialize_zammad_client()`
      - ticket_id (int): ID of the ticket to update
      - updates (dict): Partial fields to update. Supported keys:
          - title (str)
          - group_id (int > 0)
          - priority_id (int > 0)
          - customer_id (int > 0)
          - state_id (int > 0)
          - state (str) — human name; we resolve to `state_id`
          - article (dict): {subject, body, type="note", internal=false}

    Return:
      - dict: Minimal serialized ticket as returned by `_ticket_to_dict()`

    Side effects:
      - May perform a raw HTTP PUT to Zammad as a fallback if SDK signatures
        do not mutate fields as expected.
    """
    try:
        params: dict = {}
        # Whitelist known-safe fields; ignore non-positive IDs that can cause validation issues
        if "title" in updates and updates["title"] is not None:
            params["title"] = updates["title"]
        # Numeric fields: coerce to int, include only if > 0
        for key in ("group_id", "priority_id", "customer_id"):
            if key in updates and updates[key] is not None:
                try:
                    iv = int(updates[key])
                    if iv > 0:
                        params[key] = iv
                except Exception:
                    # Skip invalid numeric values silently
                    pass

        # State handling: prefer explicit state_id; else map from state name
        if "state_id" in updates and updates["state_id"] is not None:
            try:
                sid_val = int(updates["state_id"])
                if sid_val > 0:
                    params["state_id"] = sid_val
            except Exception:
                pass
        elif "state" in updates and updates["state"]:
            sid = find_state_id_by_name(client_obj, str(updates["state"]))
            if sid:
                params["state_id"] = sid

        # Optional article update (append a note)
        if "article" in updates and isinstance(updates["article"], dict):
            art = updates["article"]
            body_val = (art.get("body") or "").strip()
            if not body_val:
                # Zammad often requires a non-empty body on updates
                body_val = "Updated via API"
            params["article"] = {
                "subject": art.get("subject") or "Update",
                "body": body_val,
                "type": art.get("type") or "note",
                "internal": bool(art.get("internal", False)),
            }

        if not params:
            # No-op; return current state
            return get_ticket(client_obj, ticket_id)

        # Attempt multiple update signatures for compatibility (always pass id argument)
        update_attempts = []
        updated = None
        need_article = False

        # v1: kwargs fields (no params wrapper) — some SDKs don't support this
        try:
            updated = client_obj.ticket.update(id=ticket_id, **params)
        except Exception as e:
            update_attempts.append(f"v1(kwargs): {e}")

        # v2: positional id + kwargs
        if updated is None:
            try:
                updated = client_obj.ticket.update(ticket_id, **params)
            except Exception as e:
                update_attempts.append(f"v2(positional+kwargs): {e}")

        # v3: params= wrapper (kwargs)
        if updated is None:
            try:
                updated = client_obj.ticket.update(id=ticket_id, params=params)
            except Exception as e:
                update_attempts.append(f"v3(kwargs params=): {e}")
                if "article body" in str(e).lower():
                    need_article = True

        # v4: positional id + params=
        if updated is None:
            try:
                updated = client_obj.ticket.update(ticket_id, params=params)
            except Exception as e:
                update_attempts.append(f"v4(positional params=): {e}")
                if "article body" in str(e).lower():
                    need_article = True

        # If API requires an article and body is missing/empty, retry with a minimal note
        if updated is None and need_article and ("article" not in params or not (params["article"].get("body") or "").strip()):
            params["article"] = {
                "subject": params.get("article", {}).get("subject") or "Update",
                "body": "Updated via API",
                "type": params.get("article", {}).get("type") or "note",
                "internal": bool(params.get("article", {}).get("internal", False)),
                "content_type": "text/plain",
            }
            try:
                updated = client_obj.ticket.update(id=ticket_id, params=params)
            except Exception as e:
                update_attempts.append(f"retry(params with article): {e}")
            if updated is None:
                try:
                    updated = client_obj.ticket.update(ticket_id, params=params)
                except Exception as e:
                    update_attempts.append(f"retry(positional params with article): {e}")

        # v5: dict body including id
        if updated is None:
            try:
                body = {"id": ticket_id, **params}
                updated = client_obj.ticket.update(body)
            except Exception as e:
                update_attempts.append(f"v5(dict body): {e}")

        # If SDK calls didn't error but also didn't mutate, use raw HTTP as a last resort
        if updated is None:
            try:
                updated = _http_update_ticket(ticket_id, params)
            except Exception as e:
                update_attempts.append(f"raw_http: {e}")

        # Fetch and return latest ticket state (avoid stale/cached SDK objects)
        latest = get_ticket(client_obj, ticket_id)

        # If a title was requested to change but did not, include diagnostics
        if "title" in params and params["title"] and latest.get("title") != params["title"]:
            diag = "; ".join(update_attempts) or "no attempts captured"
            raise RuntimeError(f"Update applied but title not mutated; attempts: {diag}")

        return latest
    except Exception as e:
        raise RuntimeError(f"Failed to update ticket {ticket_id}: {e}")

def _http_update_ticket(ticket_id: int, params: dict) -> dict:
    """
    Low-level HTTP PUT update to Zammad REST API as a fallback.

    Why: Some zammad_py versions accept different update signatures or may not
    mutate fields despite returning a success envelope. This ensures updates
    (e.g., `title`) are applied.

    Returns the updated ticket JSON.
    """
    ZAMMAD_URL = os.getenv('ZAMMAD_URL')
    if not ZAMMAD_URL:
        raise ValueError("ZAMMAD_URL not set for raw HTTP update")

    base = ZAMMAD_URL.rstrip('/')
    # Avoid duplicating /api/v1 if caller provided it in ZAMMAD_URL
    if base.endswith('/api/v1') or base.endswith('/api') or '/api/' in base:
        url = f"{base}/tickets/{ticket_id}"
    else:
        url = f"{base}/api/v1/tickets/{ticket_id}"
    headers = {"Content-Type": "application/json"}

    token = os.getenv('ZAMMAD_HTTP_TOKEN')
    username = os.getenv('ZAMMAD_USERNAME')
    password = os.getenv('ZAMMAD_PASSWORD')

    auth = None
    if token:
        headers["Authorization"] = f"Token token={token}"
    elif username and password:
        auth = (username, password)
    else:
        raise ValueError("No Zammad credentials available for raw HTTP update")

    # Build payload and ensure article has content_type
    payload = {"id": ticket_id, **params}
    if isinstance(payload.get("article"), dict) and "content_type" not in payload["article"]:
        payload["article"]["content_type"] = "text/plain"

    # Try PUT first
    resp = requests.put(url, json=payload, headers=headers, auth=auth, timeout=15)
    if resp.status_code in (400, 422):
        # If server complains about article, add minimal article and retry once
        body_lower = (resp.text or "").lower()
        if "article" in body_lower and "body" in body_lower and ("article" not in payload or not (payload["article"].get("body") or "").strip()):
            payload["article"] = {
                "subject": payload.get("article", {}).get("subject") or "Update",
                "body": "Updated via API",
                "type": payload.get("article", {}).get("type") or "note",
                "internal": bool(payload.get("article", {}).get("internal", False)),
                "content_type": "text/plain",
            }
            resp = requests.put(url, json=payload, headers=headers, auth=auth, timeout=15)

    # Fallback to PATCH if PUT not accepted
    if resp.status_code in (405, 415, 422):
        resp = requests.patch(url, json=payload, headers=headers, auth=auth, timeout=15)

    try:
        resp.raise_for_status()
    except requests.HTTPError as http_err:
        # Include server body for diagnostics
        raise requests.HTTPError(f"{http_err}; status={resp.status_code}; body={resp.text}") from None

    data = resp.json() if resp.content else {}
    return data if isinstance(data, dict) else {"raw": data}

def delete_ticket(client_obj, ticket_id: int) -> dict:
    """
    Delete (or close) a ticket with robust fallbacks:
    1) Try hard delete via ticket.destroy
    2) If that fails (permissions, validations), set state to 'closed' using state_id
       discovered dynamically; fallback to 4 per memory note.
    Returns a dict with success flag and optional message.
    """
    # Try destroy
    try:
        try:
            res = client_obj.ticket.destroy(id=ticket_id)
        except Exception:
            res = client_obj.ticket.destroy(ticket_id)
        # Many clients return True/None/{} for successful destroy
        return {"success": True, "message": "Ticket destroyed"}
    except Exception as destroy_err:
        # Fallback to closing by state_id
        try:
            closed_id = find_closed_state_id(client_obj)
            updated = update_ticket(client_obj, ticket_id, {"state_id": closed_id})
            return {"success": True, "message": "Ticket closed", "ticket": updated}
        except Exception as close_err:
            raise RuntimeError(f"Failed to delete/close ticket: destroy_error={destroy_err}; close_error={close_err}")

def validate_email(email: str) -> bool:
    """Basic email validation"""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def find_customer_by_email(client_obj, email: str) -> dict:
    """
    Search for a customer by email using multiple search methods.
    Returns the customer data if found, None otherwise.
    """
    try:
        # Try direct search with email
        search_query = f'email:"{email}"'
        users = list(client_obj.user.search(search_query))
        
        if users:
            return users[0]
            
        # If not found, try a more general search
        users = list(client_obj.user.search(email))
        for user in users:
            if user.get('email', '').lower() == email.lower():
                return user
                
        return None
        
    except Exception as e:
        print(f"Warning: Error searching for customer: {str(e)}")
        return None

def find_or_create_customer(client_obj, email: str, firstname: str = None, lastname: str = None) -> int:
    """
    Searches for a customer by email. If not found, creates a new customer.
    Returns the customer ID or None if creation fails.
    
    Args:
        client_obj: Zammad API client instance
        email: Customer email address
        firstname: Customer first name (optional)
        lastname: Customer last name (optional)
        
    Returns:
        int: Customer ID if successful, None otherwise
    """
    if not email or not isinstance(email, str):
        print("Error: Email is required and must be a string")
        return None
        
    email = email.strip().lower()
    if not validate_email(email):
        print(f"Error: Invalid email format: {email}")
        return None

    try:
        # First try to find existing customer
        search_query = f'email:"{email}"'
        users = list(client_obj.user.search(search_query))
        
        if users:
            existing_customer = users[0]
            customer_id = existing_customer.get('id')
            if not customer_id:
                raise ValueError("Invalid response: Missing customer ID")
                
            print(f"Customer '{email}' found with ID: {customer_id}")
            return customer_id
            
        # If we get here, customer doesn't exist - create new one
        print(f"Customer '{email}' not found. Creating new customer...")
        
        # Prepare customer data with defaults if needed
        firstname = (firstname or "").strip() or "Unknown"
        lastname = (lastname or "").strip() or "User"
        
        new_customer_params = {
            "email": email,
            "firstname": firstname,
            "lastname": lastname,
            "roles": ["Customer"],
            "active": True,
            "verified": True
        }
        
        # Try to create the customer
        try:
            new_customer = client_obj.user.create(params=new_customer_params)
            if not new_customer or 'id' not in new_customer:
                raise ValueError("Invalid response when creating customer")
                
            customer_id = new_customer['id']
            print(f"New customer '{email}' successfully created with ID: {customer_id}")
            return customer_id
            
        except Exception as create_error:
            # If creation fails with email conflict, try to find the customer again
            error_msg = str(create_error).lower()
            if "already used" in error_msg or "already exists" in error_msg:
                print("Customer creation failed - email already in use. Searching again...")
                existing_customer = find_customer_by_email(client_obj, email)
                if existing_customer and 'id' in existing_customer:
                    print(f"Found existing customer with ID: {existing_customer['id']}")
                    return existing_customer['id']
            
            # If we get here, we couldn't find or create the customer
            print(f"Failed to create customer: {str(create_error)}")
            return None

    except Exception as e:
        print(f"Error in find_or_create_customer: {str(e)}")
        return None

def create_ticket_flow(client_obj, interactive=False):
    """
    Function to create a new Zammad ticket, with classification option.
    If interactive is True, it will prompt for user input.
    """
    print("\n--- Create New Ticket ---")
    if interactive:
        customer_email = input("Enter customer email: ").strip()
        customer_firstname = input("Enter customer first name: ").strip()
        customer_lastname = input("Enter customer last name: ").strip()
        ticket_title = input("Enter ticket title: ").strip()
        ticket_body = input("Enter ticket description/body: ").strip()
    else:
        # Dummy data for non-interactive mode
        customer_email = "test@example.com"
        customer_firstname = "Test"
        customer_lastname = "User"
        ticket_title = "My computer is slow"
        ticket_body = "My computer is running very slowly, and I can't open applications."

    customer_id = find_or_create_customer(client_obj, customer_email, customer_firstname, customer_lastname)

    if not customer_id:
        print("Could not determine customer ID. Aborting ticket creation.")
        return

    # Default values for department and priority
    classified_department = "Unknown"
    classified_priority = "Unknown"
    
    print("\nProceeding without automatic classification.")


    # --- Group Selection ---
    groups_map = get_all_groups(client_obj)
    selected_group_id = None
    if groups_map:
        if classified_department != "Unknown" and classified_department in groups_map:
            selected_group_id = groups_map[classified_department]
            print(f"Using classified group: {classified_department} (ID: {selected_group_id})")
        else:
            if interactive:
                while selected_group_id is None:
                    group_name_input = input("Enter desired group (department) name for the ticket: ").strip()
                    selected_group_id = groups_map.get(group_name_input)
                    if selected_group_id is None:
                        create_choice = input("Group not found. Would you like to create it? (yes/no): ").strip().lower()
                        if create_choice in ("yes", "y"):
                            try:
                                new_group = client_obj.group.create(params={
                                    "name": group_name_input,
                                    "active": True,
                                    "assignment_timeout": 0
                                })
                                selected_group_id = new_group.get("id")
                                if selected_group_id:
                                    groups_map[group_name_input] = selected_group_id
                                    print(f"Created new group '{group_name_input}' with ID: {selected_group_id}")
                                else:
                                    print("Failed to retrieve new group ID. Please try again.")
                            except Exception as e:
                                print(f"Failed to create group: {e}")
                        else:
                            print("Please choose from the existing groups listed above.")
            else:
                # Default to the first group if not interactive and classification fails
                selected_group_id = next(iter(groups_map.values()), 1)
    else:
        print("No groups available. Defaulting to group ID 1.")
        selected_group_id = 1

    # --- Priority Selection ---
    priority_id = 2  # Default to normal priority
    if classified_priority != "Unknown":
        priority_mapping = {"low": 1, "normal": 2, "high": 3}
        priority_id = priority_mapping.get(classified_priority.lower(), 2)
    elif interactive:
        while True:
            try:
                p_input = input("Enter priority (1: Low, 2: Normal, 3: High) [2]: ").strip()
                if not p_input:
                    priority_id = 2
                    break
                p_id = int(p_input)
                if 1 <= p_id <= 3:
                    priority_id = p_id
                    break
                else:
                    print("Invalid priority. Please enter a number between 1 and 3.")
            except ValueError:
                print("Invalid input. Please enter a number.")

    # --- Create Ticket ---
    try:
        ticket_params = {
            "title": ticket_title,
            "group_id": selected_group_id,
            "customer_id": customer_id,
            "priority_id": priority_id,
            "article": {
                "subject": ticket_title,
                "body": ticket_body,
                "type": "note",
                "internal": False,
            },
        }

        print("\nAttempting to create a new ticket...")
        ticket = client_obj.ticket.create(params=ticket_params)
        
        print(f"Successfully created ticket with ID: {ticket['id']}")
        print(f"Ticket Number: {ticket['number']}")
        print(json.dumps(ticket, indent=2))
        return ticket

    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP Error during ticket creation: {http_err}")
        if http_err.response is not None:
            body_text = http_err.response.text
            print(f"Response body: {body_text}")
            # If not authorized for the selected group, retry with group_id 1
            if "not authorized" in body_text.lower():
                try:
                    print("Retrying ticket creation in default group ID 1 ...")
                    ticket_params["group_id"] = 1
                    ticket = client_obj.ticket.create(params=ticket_params)
                    print(f"Successfully created ticket with ID: {ticket['id']}")
                    print(f"Ticket Number: {ticket['number']}")
                    print(json.dumps(ticket, indent=2))
                    return ticket
                except Exception as retry_err:
                    print(f"Retry failed: {retry_err}")
    except Exception as e:
        err_msg = str(e)
        if "not authorized" in err_msg.lower():
            try:
                print("Error indicates authorization issue. Retrying ticket creation in default group ID 1 ...")
                ticket_params["group_id"] = 1
                ticket = client_obj.ticket.create(params=ticket_params)
                print(f"Successfully created ticket with ID: {ticket['id']}")
                print(f"Ticket Number: {ticket['number']}")
                print(json.dumps(ticket, indent=2))
                return ticket
            except Exception as retry_err:
                print(f"Retry failed: {retry_err}")
        else:
            print(f"An unexpected error occurred during ticket creation: {e}")
    return None

def main():
    """
    Main function to run the Zammad integration script.
    """
    print("🚀 Starting Zammad Integration Script")
    print("=" * 60)

    # Initialize the client for CLI/script usage only
    try:
        local_client = initialize_zammad_client()
    except Exception as e:
        print(f"Error: {e}")
        return

    create_ticket_flow(local_client, interactive=True)

    print("\n✅ Zammad Integration Script finished!")

if __name__ == "__main__":
    main()