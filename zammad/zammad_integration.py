import os
import json
import requests
from dotenv import load_dotenv, find_dotenv
from zammad_py import ZammadAPI 
from Model.evaluation import ITTicketEvaluator
from typing import Dict, List

# Load environment variables from .env file
load_dotenv()

# --- 1. Zammad API Client Initialization ---
ZAMMAD_URL = os.getenv('ZAMMAD_URL')
ZAMMAD_HTTP_TOKEN = os.getenv('ZAMMAD_HTTP_TOKEN')
ZAMMAD_USERNAME = os.getenv('ZAMMAD_USERNAME')
ZAMMAD_PASSWORD = os.getenv('ZAMMAD_PASSWORD')

client = None
try:
    if ZAMMAD_HTTP_TOKEN:
        client = ZammadAPI(url=ZAMMAD_URL, http_token=ZAMMAD_HTTP_TOKEN, username=ZAMMAD_USERNAME, password=ZAMMAD_PASSWORD)
    elif ZAMMAD_USERNAME and ZAMMAD_PASSWORD:
        client = ZammadAPI(url=ZAMMAD_URL, username=ZAMMAD_USERNAME, password=ZAMMAD_PASSWORD)
    else:
        raise ValueError("Zammad credentials (HTTP_TOKEN or USERNAME/PASSWORD) not found in environment variables.")
    
    # Test connection by getting current user info
    current_user = client.user.me()
    print(f"Successfully connected to Zammad as: {current_user.get('email')}")
    
    # Verify user has required permissions
    if not hasattr(client.user, 'me') or not hasattr(client.ticket, 'create'):
        raise PermissionError("Current user lacks required permissions to create tickets")

except PermissionError as pe:
    print(f"Permission Error: {pe}")
    print("Please ensure your account has 'ticket.agent' role in Zammad")
    exit(1)
except Exception as e:
    print(f"Failed to initialize Zammad client: {e}")
    exit(1)

# --- Hugging Face Model Initialization for Classification ---
HF_MODEL_ID = os.getenv('HF_MODEL_ID') # Get model ID from environment
HF_TOKEN = os.getenv('HF_TOKEN')
ticket_evaluator = None
if HF_MODEL_ID:
    try:
        ticket_evaluator = ITTicketEvaluator(model_id=HF_MODEL_ID, api_token=HF_TOKEN)
        print(f"✅ ITTicketEvaluator initialized successfully with model: {HF_MODEL_ID}")
    except Exception as e:
        print(f"❌ Failed to initialize ITTicketEvaluator: {e}")
        ticket_evaluator = None
else:
    print("⚠️ HF_MODEL_ID not found in environment variables. Classification will not be available.")


def classify_ticket_description(description: str) -> Dict[str, str]:
    """
    Classifies a ticket description using the ITTicketEvaluator.
    Returns Department and Priority.
    """
    if not ticket_evaluator:
        return {"Department": "Unknown", "Priority": "Unknown", "error": "Ticket evaluator not loaded."}

    try:
        # Use the custom classifier method from the evaluator
        results = ticket_evaluator.classify_with_custom_classifier([description])
        if not results:
            raise ValueError("Classification returned no results.")

        # Extract the first result
        classification_result = results[0]
        
        if "error" in classification_result:
            raise ValueError(classification_result["error"])

        department = classification_result.get("department", "Unknown")
        priority = classification_result.get("priority", "Unknown")
        
        return {"Department": department, "Priority": priority}

    except Exception as e:
        print(f"Error during classification: {e}")
        return {"Department": "Unknown", "Priority": "Unknown", "error": str(e)}

def get_all_groups(client_obj) -> Dict[str, int]:
    """
    Retrieves all Zammad groups and returns a dictionary mapping group names to IDs.
    """
    groups_map = {}
    try:
        all_groups_pagination = client_obj.group.all()
        all_groups_list = list(all_groups_pagination)
        if all_groups_list:
            print("\n--- Available Zammad Groups (Departments) ---")
            for group in all_groups_list:
                group_id = group.get('id')
                group_name = group.get('name')
                if group_id and group_name:
                    groups_map[group_name] = group_id
                    print(f"  ID: {group_id}, Name: {group_name}")
            print("---------------------------------------------")
        else:
            print("No groups found in your Zammad instance.")
    except Exception as e:
        print(f"An error occurred while retrieving groups: {e}")
    return groups_map

def find_or_create_customer(client_obj, email: str, firstname: str, lastname: str) -> int:
    """
    Searches for a customer by email. If not found, creates a new customer.
    Returns the customer ID.
    """
    customer_id = None
    try:
        # --- Part 1: Ensure Customer Exists (Search or Create) ---
        print(f"Searching for customer: {email}...")

        search_query_string = f'email:"{email}"'
        existing_users_pagination = client_obj.user.search(search_query_string)
        existing_customers = list(existing_users_pagination)

        if existing_customers:
            exact_match_customer = next((user for user in existing_customers if user.get('email') == email), None)

            if exact_match_customer:
                customer_id = exact_match_customer['id']
                print(f"Customer '{email}' already exists with ID: {customer_id}")
            else:
                print(f"Customer '{email}' not found via exact email match in search results.")
        else:
            print(f"No customers found matching '{email}'.")


        if customer_id is None:
            print(f"Customer '{email}' not found. Creating new customer...")
            new_customer_params = {
                "email": email,
                "firstname": firstname,
                "lastname": lastname,
                "roles": ["Customer"]
            }
            new_customer = client_obj.user.create(params=new_customer_params)
            customer_id = new_customer['id']
            print(f"New customer '{email}' successfully created with ID: {customer_id}")
        else:
            print(f"Proceeding with existing customer ID: {customer_id}")

    except Exception as e:
        print(f"An error occurred during customer search/creation: {e}")
        return None # Return None on error
        
    return customer_id

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

    customer_id = find_or_create_customer(client_obj, customer_email, customer_firstname, customer_lastname)

    if not customer_id:
        print("Could not determine customer ID. Aborting ticket creation.")
        return



    classified_department = "Unknown"
    classified_priority = "Unknown"

    # --- Classification Step ---
    if ticket_evaluator:
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
                    classified_department = "Unknown" # Reset if not accepted
                    classified_priority = "Unknown"
                    print("Using manual input for Department and Priority.")
                else:
                    print("Using classified Department and Priority.")
            else:
                print("Using classified Department and Priority.")
        else:
            print(f"Classification failed: {classification_result.get('error', 'Unknown error')}")
            print("Proceeding without classification.")
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
                        print("Invalid group name. Please choose from the list above or enter a valid name.")
            else:
                selected_group_id = 1 # Default to group 1 if not found
    else:
        print("No groups available. Defaulting to group ID 1 (if it exists).")
        selected_group_id = 1 # Fallback to default group ID if no groups found

    # --- Priority Selection (if not classified or not accepted) ---
    priority_id = 2 # Default to normal priority
    if classified_priority != "Unknown":
        # Map classified priority to Zammad priority ID (assuming common mappings)
        priority_mapping = {
            "low": 1,
            "normal": 2,
            "high": 3,
        }
        priority_id = priority_mapping.get(classified_priority.lower(), 2) # Default to normal if not mapped
    else:
        if interactive:
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
                        print("Invalid priority. Please enter a number between 1 and 4.")
                except ValueError:
                    print("Invalid input. Please enter a number.")
        else:
            priority_id = 2 # Default to normal

    # --- Create Ticket ---
    try:
        # Validate required fields before creating ticket
        if not ticket_title or not selected_group_id or not customer_id:
            raise ValueError("Missing required fields for ticket creation (title, group_id, or customer_id)")
            
        ticket_params = {
            "title": ticket_title,
            "group_id": selected_group_id,
            "customer_id": customer_id,
            "priority_id": priority_id,
            "article": {
                "subject": ticket_title,
                "body": ticket_body,
                "type": "email",
                "internal": False,
                "to": customer_email
            },
            "state_id": 1
        }

        print("\nAttempting to create a new ticket...")
        try:
            ticket = client_obj.ticket.create(params=ticket_params)
            
            print(f"Successfully created ticket with ID: {ticket['id']}")
            print(f"Ticket Number: {ticket['number']}")
            print(f"Ticket Title: {ticket['title']}")
            print("\n--- Full JSON of Created Ticket ---")
            print(json.dumps(ticket, indent=2))
            print("--- End of Full JSON ---")
            return ticket
        except requests.exceptions.HTTPError as http_err:
            if http_err.response.status_code == 401:
                print("\n⚠️ Authorization failed. Possible causes:")
                print("1. Invalid credentials or expired token")
                print("2. Missing 'ticket.agent' role for your user")
                print("3. Insufficient permissions for the requested operation")
                print(f"\nError details: {http_err}")
            elif http_err.response.status_code == 422:
                print("\n⚠️ Validation error. Please check your ticket parameters:")
                print(f"Error details: {http_err.response.json()}")
            else:
                print(f"\n⚠️ HTTP Error during ticket creation: {http_err}")
            return None
        except Exception as api_error:
            print(f"\n⚠️ API error during ticket creation: {api_error}")
            if hasattr(api_error, 'response') and hasattr(api_error.response, 'text'):
                print(f"Response details: {api_error.response.text}")
            return None
    except ValueError as ve:
        print(f"\n⚠️ Validation Error: {ve}")
        return None
    except Exception as e:
        print(f"\n⚠️ An unexpected error occurred during ticket creation: {e}")
        return None

def main():
    """
    Main function to run the Zammad integration script.
    """
    print("🚀 Starting Zammad Integration Script")
    print("=" * 60)

    # Run the interactive ticket creation flow
    create_ticket_flow(client, interactive=True)

    print("\n✅ Zammad Integration Script finished!")


if __name__ == "__main__":
    main()


