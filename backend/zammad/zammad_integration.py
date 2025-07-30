import os
import json
import requests
from dotenv import load_dotenv, find_dotenv
from zammad_py import ZammadAPI
from groq import Groq
from typing import Dict

# Load environment variables from .env file
load_dotenv()

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
        if ZAMMAD_HTTP_TOKEN:
            client = ZammadAPI(url=ZAMMAD_URL, http_token=ZAMMAD_HTTP_TOKEN)
        elif ZAMMAD_USERNAME and ZAMMAD_PASSWORD:
            client = ZammadAPI(url=ZAMMAD_URL, username=ZAMMAD_USERNAME, password=ZAMMAD_PASSWORD)
        else:
            raise ValueError("Zammad credentials not found. Set either ZAMMAD_HTTP_TOKEN or both ZAMMAD_USERNAME and ZAMMAD_PASSWORD")

        # Test connection
        current_user = client.user.me()
        if not current_user or 'email' not in current_user:
            raise ValueError("Failed to authenticate with Zammad: Invalid response from server")
            
        print(f"Successfully connected to Zammad as: {current_user.get('email')}")
        return client

    except Exception as e:
        raise RuntimeError(f"Failed to initialize Zammad client: {str(e)}")

# Initialize the client
try:
    client = initialize_zammad_client()
except Exception as e:
    print(f"Error: {e}")
    exit(1)

# --- Groq API Client Initialization for Classification ---
GROQ_API_KEY = os.getenv('GROQ_API_KEY')
groq_client = None
if GROQ_API_KEY:
    try:
        groq_client = Groq(api_key=GROQ_API_KEY)
        print(" Groq client initialized successfully.")
    except Exception as e:
        print(f"Failed to initialize Groq client: {e}")
else:
    print("GROQ_API_KEY not found in environment variables. Classification will not be available.")


def classify_ticket_description(description: str) -> Dict[str, str]:
    """
    Classifies a ticket description using the Groq API.
    Returns Department and Priority.
    """
    if not groq_client:
        return {"Department": "Unknown", "Priority": "Unknown", "error": "Groq client not loaded."}

    try:
        completion = groq_client.chat.completions.create(
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Classify the following IT ticket and return output in JSON format with keys: "
                        "'Department', 'Priority'.\n\n"
                        f"Ticket: \"{description}\"\n\n"
                        "departments = [\n"
                        "    \"IT\",\n"
                        "    \"Human Resources\",\n"
                        "    \"Finance\",\n"
                        "    \"Sales\",\n"
                        "    \"Marketing\",\n"
                        "    \"Operations\",\n"
                        "    \"Customer Service\",\n"
                        "    \"Legal\",\n"
                        "    \"Product Development\",\n"
                        "    \"Facilities\"\n"
                        "]\n"
                        "priority = [\"Low\", \"Normal\", \"High\"]\n"
                        "only json format."
                    )
                },
                {
                    "role": "user",
                    "content": description
                }
            ],
            temperature=0,
            max_tokens=1024,
            top_p=1,
            stream=False,
            response_format={"type": "json_object"},
        )
        
        response_content = completion.choices[0].message.content
        classification_result = json.loads(response_content)
        
        department = classification_result.get("Department", "Unknown")
        priority = classification_result.get("Priority", "Unknown")
        
        return {"Department": department, "Priority": priority}

    except Exception as e:
        print(f"Error during classification: {e}")
        return {"Department": "Unknown", "Priority": "Unknown", "error": str(e)}

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

    classified_department = "Unknown"
    classified_priority = "Unknown"

    # --- Classification Step ---
    if groq_client:
        print("\nAttempting to classify ticket description...")
        classification_result = classify_ticket_description(ticket_body)
        
        if "error" not in classification_result:
            classified_department = classification_result.get("Department", "Unknown")
            classified_priority = classification_result.get("Priority", "Unknown")
            print(f"Classified Department: {classified_department}")
            print(f"Classified Priority: {classified_priority}")
            
            if interactive:
                use_classified = input("Use classified Department and Priority? (yes/no): ").strip().lower()
                if use_classified != 'yes':
                    classified_department = "Unknown"
                    classified_priority = "Unknown"
                    print("Using manual input for Department and Priority.")
        else:
            print(f"Classification failed: {classification_result.get('error', 'Unknown error')}")
    else:
        print("Classification model not available. Proceeding without classification.")

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

    create_ticket_flow(client, interactive=True)

    print("\n✅ Zammad Integration Script finished!")

if __name__ == "__main__":
    main()