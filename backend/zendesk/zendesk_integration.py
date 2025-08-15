import os
import os
import json
import requests
from dotenv import load_dotenv
from zenpy import Zenpy
from zenpy.lib.api_objects import Ticket, User, Group, GroupMembership
from pathlib import Path

class ZendeskIntegration:
    def __init__(self):
        # Load .env from backend directory (and common fallbacks)
        # Priority: backend/.env -> project_root/.env -> CWD/.env
        try:
            env_paths = [
                Path(__file__).resolve().parents[1] / ".env",  # backend/.env
                Path(__file__).resolve().parents[2] / ".env",  # repo root .env
                Path.cwd() / ".env",                           # current working dir
            ]
            for p in env_paths:
                if p.exists():
                    load_dotenv(dotenv_path=p, override=False)
        except Exception:
            # Fallback to default search if anything goes wrong
            load_dotenv()
        
        # Load and validate Zendesk credentials
        self.zendesk_email = os.getenv('ZENDESK_EMAIL')
        self.zendesk_token = os.getenv('ZENDESK_TOKEN')
        self.zendesk_subdomain = os.getenv('ZENDESK_SUBDOMAIN')
        
        # Validate that all required credentials are present
        missing_creds = []
        if not self.zendesk_email:
            missing_creds.append('ZENDESK_EMAIL')
        if not self.zendesk_token:
            missing_creds.append('ZENDESK_TOKEN')
        if not self.zendesk_subdomain:
            missing_creds.append('ZENDESK_SUBDOMAIN')
            
        if missing_creds:
            raise ValueError(f"Missing required Zendesk credentials: {', '.join(missing_creds)}. Please check your .env file.")
        
        # Print credential status (without exposing sensitive data)
        print(f"✅ Zendesk credentials loaded:")
        print(f"   Email: {self.zendesk_email}")
        print(f"   Subdomain: {self.zendesk_subdomain}")
        print(f"   Token: {'*' * (len(self.zendesk_token) - 4) + self.zendesk_token[-4:] if len(self.zendesk_token) > 4 else '***'}")
        
        creds = {
            'email': self.zendesk_email,
            'token': self.zendesk_token,
            'subdomain': self.zendesk_subdomain
        }
        
        try:
            self.zenpy_client = Zenpy(**creds)
            print("✅ Zendesk client initialized successfully")
        except Exception as e:
            print(f"❌ Failed to initialize Zendesk client: {e}")
            raise e
        
        # --- FastAPI Ticket Classifier Service URL ---
        self.API_URL = "http://127.0.0.1:8000/api/v1/"
        self.PREDICT_URL = f"{self.API_URL}predict"
        self.HEALTH_URL = f"{self.API_URL}health"
        
        # Note: This implementation uses the local FastAPI ticket classifier service
        # instead of the GROQ API for ticket classification

    def classify_ticket_description(self, description: str):
        """
        Classifies a ticket description using the FastAPI classifier service.
        Returns Department and Priority.
        """
        try:
            payload = {"description": description}
            response = requests.post(self.PREDICT_URL, json=payload)
            response.raise_for_status()
            
            classification_result = response.json()
            department = classification_result.get("department", "Unknown")
            priority = classification_result.get("priority", "Unknown")
            
            return {"Department": department, "Priority": priority}

        except requests.exceptions.RequestException as e:
            print(f"Error during classification: {e}")
            return {"Department": "Unknown", "Priority": "Unknown", "error": f"Failed to connect to classifier API: {str(e)}"}
        except Exception as e:
            print(f"Error during classification: {e}")
            return {"Department": "Unknown", "Priority": "Unknown", "error": str(e)}

    def test_authentication(self):
        """
        Test Zendesk authentication by making a simple API call.
        Returns True if authentication is successful, False otherwise.
        """
        try:
            # Try to get current user info to test authentication
            current_user = self.zenpy_client.users.me()
            
            # Check if we're getting anonymous user (indicates auth issue)
            if current_user.name == "Anonymous user" or current_user.email == "invalid@example.com":
                print("⚠️  Warning: Connected as anonymous user. This indicates an authentication issue.")
                print("   Possible causes:")
                print("   1. Invalid API token")
                print("   2. Token doesn't have sufficient permissions")
                print("   3. Email doesn't match the token owner")
                print("   4. Account is suspended or inactive")
                return False
            
            print(f"✅ Authentication successful! Connected as: {current_user.name} ({current_user.email})")
            return True
        except Exception as e:
            print(f"❌ Authentication failed: {e}")
            print("\n🔍 Troubleshooting tips:")
            print("1. Check if your .env file contains the correct Zendesk credentials:")
            print("   ZENDESK_EMAIL=your-email@domain.com")
            print("   ZENDESK_TOKEN=your-api-token")
            print("   ZENDESK_SUBDOMAIN=your-subdomain")
            print("2. Verify your API token is valid and has the necessary permissions")
            print("3. Ensure your subdomain is correct (e.g., 'company' for company.zendesk.com)")
            print("4. Check if your Zendesk account is active and not suspended")
            return False

    def _serialize_ticket_response(self, ticket_response):
        """
        Safely serialize Zendesk ticket response to avoid JSON parsing errors.
        """
        try:
            if hasattr(ticket_response, 'ticket'):
                ticket = ticket_response.ticket
                return {
                    "success": True,
                    "ticket_id": getattr(ticket, 'id', None),
                    "ticket_subject": getattr(ticket, 'subject', None),
                    "ticket_status": getattr(ticket, 'status', None),
                    "ticket_priority": getattr(ticket, 'priority', None),
                    "message": "Ticket created successfully!"
                }
            else:
                return {
                    "success": True,
                    "ticket_data": str(ticket_response),
                    "message": "Ticket created successfully!"
                }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to serialize ticket response: {str(e)}"
            }

    def search_user(self, email):
        users = list(self.zenpy_client.users.search(f"email:{email}"))
        if users:
            print(f"User with email '{email}' found.")
            return users[0]
        return None

    def find_or_create_group(self, group_name):
        """
        Find an existing group by name or create a new one if it doesn't exist.
        Returns the group object with its ID.
        """
        try:
            # Search for existing group by name
            groups = list(self.zenpy_client.groups())
            for group in groups:
                if group.name.lower() == group_name.lower():
                    print(f"Found existing group: {group.name} (ID: {group.id})")
                    return group
            
            # Group doesn't exist, create a new one
            print(f"Creating new group: {group_name}")
            new_group = Group(name=group_name)
            created_group = self.zenpy_client.groups.create(new_group)
            print(f"Created group: {created_group.name} (ID: {created_group.id})")
            return created_group
            
        except Exception as e:
            print(f"Error finding or creating group '{group_name}': {e}")
            return None

    def ensure_agent_role(self, user):
        """
        Ensure the given user has 'agent' role. If not, try to upgrade the role.
        Handles MaxAgentExceeded gracefully.
        Returns True if user is an agent (after ensuring), else False.
        """
        try:
            if getattr(user, 'role', None) == 'agent':
                return True
            # Try to upgrade the role to agent
            original_role = getattr(user, 'role', None)
            user.role = 'agent'
            try:
                updated = self.zenpy_client.users.update(user)
                print(f"Upgraded user '{user.email}' from role '{original_role}' to 'agent'.")
                return True
            except Exception as e:
                error_str = str(e)
                if 'MaxAgentExceeded' in error_str:
                    print(f"⚠️ Agent limit exceeded. Cannot upgrade user '{user.email}' to agent.")
                    return False
                print(f"❌ Failed to upgrade user '{user.email}' to agent: {error_str}")
                return False
        except Exception as e:
            print(f"❌ Error ensuring agent role for '{getattr(user, 'email', 'unknown')}': {e}")
            return False

    def ensure_user_in_group(self, user_id, group_id):
        """
        Ensure the user is a member of the specified group. If not, create the membership.
        Returns True if membership exists or was created; False otherwise.
        """
        try:
            # Check existing memberships for the user
            memberships = []
            try:
                memberships = list(self.zenpy_client.group_memberships(user=user_id))
            except Exception:
                # Fallback: some Zenpy versions may not accept the filter param
                memberships = list(self.zenpy_client.group_memberships())
            for m in memberships:
                if getattr(m, 'group_id', None) == group_id and getattr(m, 'user_id', None) == user_id:
                    print(f"User {user_id} already a member of group {group_id}.")
                    return True
            # Create membership
            gm = GroupMembership(user_id=user_id, group_id=group_id)
            self.zenpy_client.group_memberships.create(gm)
            print(f"Added user {user_id} to group {group_id}.")
            return True
        except Exception as e:
            print(f"❌ Failed to ensure group membership for user {user_id} in group {group_id}: {e}")
            return False

    def create_user(self, email, name, role):
        print(f"Creating a new user with email '{email}' with role '{role}'.")
        try:
            user = User(name=name, email=email, role=role)
            return self.zenpy_client.users.create(user)
        except Exception as e:
            error_str = str(e)
            if "MaxAgentExceeded" in error_str and role == 'agent':
                print(f"⚠️ Agent limit exceeded. Cannot create agent user '{email}'. Ticket will be created without assignee.")
                return None
            else:
                print(f"❌ Failed to create user '{email}': {error_str}")
                raise e

    def create_ticket_with_classification(self, customer_email, customer_name, assignee_email, assignee_name, ticket_subject, ticket_description, auto_proceed=True):
        """
        Creates a new ticket with automated classification of priority and department.
        
        Args:
            auto_proceed (bool): If True, automatically proceed with AI classification without user confirmation
        """
        customer = self.search_user(customer_email)
        if not customer:
            customer = self.create_user(customer_email, customer_name, 'end-user')

        assignee = None
        if assignee_email:
            assignee = self.search_user(assignee_email)
            if not assignee:
                try:
                    assignee = self.create_user(assignee_email, assignee_name, 'agent')
                except Exception as e:
                    print(f"⚠️ Could not create assignee user: {str(e)}")
                    print("Ticket will be created without assignee.")
                    assignee = None
            else:
                # Ensure the existing user is an agent; if can't upgrade, skip assignee
                if not self.ensure_agent_role(assignee):
                    print("Proceeding without assignee due to role limitations.")
                    assignee = None

        priority = "normal"
        department = "IT Support"

        print("\nAttempting to classify ticket description...")
        classification_result = self.classify_ticket_description(ticket_description)
        
        if "error" not in classification_result:
            priority = classification_result.get("Priority", "normal").lower()
            department = classification_result.get("Department", "IT Support")
            print(f"Classified Priority: {priority}")
            print(f"Classified Department: {department}")
            
            # Auto-proceed with classification in web application context
            if auto_proceed:
                print("Auto-proceeding with AI classification...")
            else:
                # This would only be used in command-line context
                print("Using AI classification results")
        else:
            print(f"Classification failed: {classification_result.get('error', 'Unknown error')}")
            print("Using default values.")

        if customer:
            # Find or create the group based on the classified department
            group = None
            group_id = None
            if department and department != "Unknown":
                group = self.find_or_create_group(department)
                if group:
                    group_id = group.id
                    print(f"Assigning ticket to group: {department} (ID: {group_id})")
                else:
                    print(f"Failed to find or create group: {department}")
            # Prepare diagnostics
            diagnostics = {
                "assignee_upgraded_to_agent": False,
                "assignee_added_to_group": False,
                "group_id": group_id,
            }

            # Ensure assignee is agent and in group BEFORE assignment
            if assignee:
                upgraded = self.ensure_agent_role(assignee)
                diagnostics["assignee_upgraded_to_agent"] = upgraded if getattr(assignee, 'role', None) != 'agent' else True
                if not upgraded:
                    print("Proceeding without assignee due to role limitations.")
                    assignee = None
                elif group_id:
                    in_group = self.ensure_user_in_group(assignee.id, group_id)
                    diagnostics["assignee_added_to_group"] = in_group
                    if not in_group:
                        print("Proceeding without assignee because adding to group failed.")
                        assignee = None

            # Create ticket with group assignment
            ticket_params = {
                "subject": ticket_subject,
                "description": ticket_description,
                "requester_id": customer.id,
                "priority": priority
            }
            
            if assignee:
                ticket_params["assignee_id"] = assignee.id
                
            if group_id:
                ticket_params["group_id"] = group_id
                
            ticket = Ticket(**ticket_params)
            created_ticket = self.zenpy_client.tickets.create(ticket)
            print(f"Ticket created successfully with ID: {created_ticket.ticket.id}")
            
            # Return a serializable response instead of the raw Zendesk object
            return {
                "success": True,
                "ticket_id": created_ticket.ticket.id,
                "ticket_subject": created_ticket.ticket.subject,
                "ticket_status": created_ticket.ticket.status,
                "requester_email": customer_email,
                "requester_name": customer_name,
                "assignee_email": assignee_email if assignee else None,
                "assignee_name": assignee_name if assignee else None,
                "priority": priority,
                "department": department,
                **diagnostics,
                "message": "Ticket created successfully!"
            }
        else:
            print("Could not create ticket. Customer not found or created.")
            return {
                "success": False,
                "error": "Could not create ticket. Customer not found or created."
            }

    def _print_ticket_details(self, ticket):
        """Helper function to print ticket details."""
        print(f"Ticket ID: {ticket.id}, Subject: {ticket.subject}, Status: {ticket.status}")
        if ticket.assignee:
            print(f"  Assignee: {ticket.assignee.name}, Email: {ticket.assignee.email}")
        if ticket.requester:
            print(f"  Requester: {ticket.requester.name}, Email: {ticket.requester.email}")
        print("-" * 20)

    def search_tickets(self, search_query):
        """
        Searches for tickets using a search query and prints the results.
        """
        print(f"\nSearching for tickets with query: '{search_query}'")
        try:
            for ticket in self.zenpy_client.search(search_query, type='ticket'):
                self._print_ticket_details(ticket)
        except Exception as e:
            print(f"An error occurred while searching for tickets: {e}")

    def view_all_tickets(self):
        """
        Retrieves and prints all tickets.
        """
        print("\nRetrieving all tickets...")
        try:
            for ticket in self.zenpy_client.tickets():
                self._print_ticket_details(ticket)
        except Exception as e:
            print(f"An error occurred while retrieving tickets: {e}")

    def view_all_customers(self):
        """
        Retrieves and prints all customers (end-users).
        """
        print("\nRetrieving all customers...")
        try:
            for customer in self.zenpy_client.users(role="end-user"):
                print(f"  Customer: {customer.name}, Email: {customer.email}")
        except Exception as e:
            print(f"An error occurred while retrieving customers: {e}")

    def view_all_assignees(self):
        """
        Retrieves and prints all assignees (agents).
        """
        print("\nRetrieving all assignees...")
        try:
            for agent in self.zenpy_client.users(role="agent"):
                print(f"  Assignee: {agent.name}, Email: {agent.email}")
        except Exception as e:
            print(f"An error occurred while retrieving assignees: {e}")

if __name__ == '__main__':
    try:
        zendesk = ZendeskIntegration()
        
        # Test authentication first
        print("\n🔐 Testing Zendesk authentication...")
        if not zendesk.test_authentication():
            print("❌ Cannot proceed without valid authentication.")
            exit(1)
        
        print("✅ Ready to use Zendesk integration!")
        
    except ValueError as e:
        print(f"❌ Configuration error: {e}")
        exit(1)
    except Exception as e:
        print(f"❌ Failed to initialize Zendesk integration: {e}")
        exit(1)

    while True:
        print("\n--- Zendesk Ticket Management ---")
        print("1. Create a new ticket")
        print("2. View tickets")
        print("3. View users")
        print("4. Test authentication")
        print("5. Exit")
        choice = input("Enter your choice (1-5): ").strip()

        if choice == '1':
            print("\n--- Create New Zendesk Ticket ---")
            customer_email = input("Enter customer email: ").strip()
            customer_name = input("Enter customer name: ").strip()
            assignee_email = input("Enter assignee email: ").strip()
            assignee_name = input("Enter assignee name: ").strip()
            ticket_subject = input("Enter ticket title: ").strip()
            ticket_description = input("Enter ticket description: ").strip()

            zendesk.create_ticket_with_classification(
                customer_email,
                customer_name,
                assignee_email,
                assignee_name,
                ticket_subject,
                ticket_description
            )
        elif choice == '2':
            while True:
                print("\n--- View Zendesk Tickets ---")
                print("1. View all tickets")
                print("2. Search by Status")
                print("3. Search by Priority")
                print("4. Search by Requester Email")
                print("5. Search by Assignee Email")
                print("6. Custom Search")
                print("7. Back to Main Menu")
                search_choice = input("Enter your choice (1-7): ").strip()

                if search_choice == '1':
                    zendesk.view_all_tickets()
                elif search_choice == '2':
                    status = input("Enter status (e.g., new, open, pending, solved): ").strip()
                    zendesk.search_tickets(f"status:{status}")
                elif search_choice == '3':
                    priority = input("Enter priority (e.g., low, normal, high): ").strip()
                    zendesk.search_tickets(f"priority:{priority}")
                elif search_choice == '4':
                    email = input("Enter requester's email: ").strip()
                    zendesk.search_tickets(f"requester:{email}")
                elif search_choice == '5':
                    email = input("Enter assignee's email: ").strip()
                    zendesk.search_tickets(f"assignee:{email}")
                elif search_choice == '6':
                    query = input("Enter custom search query: ").strip()
                    zendesk.search_tickets(query)
                elif search_choice == '7':
                    break
                else:
                    print("Invalid choice. Please enter a number between 1 and 7.")
        elif choice == '3':
            while True:
                print("\n--- View Users ---")
                print("1. View all customers")
                print("2. View all assignees")
                print("3. Back to Main Menu")
                user_choice = input("Enter your choice (1-3): ").strip()

                if user_choice == '1':
                    zendesk.view_all_customers()
                elif user_choice == '2':
                    zendesk.view_all_assignees()
                elif user_choice == '3':
                    break
                else:
                    print("Invalid choice. Please enter a number between 1 and 3.")
        elif choice == '4':
            print("\n🔐 Testing Zendesk authentication...")
            zendesk.test_authentication()
        elif choice == '5':
            print("Exiting.")
            break
        else:
            print("Invalid choice. Please enter a number between 1 and 5.")