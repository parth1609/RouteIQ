import os
import json
from dotenv import load_dotenv
from zenpy import Zenpy
from zenpy.lib.api_objects import Ticket, User
from groq import Groq

class ZendeskIntegration:
    def __init__(self):
        load_dotenv()
        creds = {
            'email': os.getenv('ZENDESK_EMAIL'),
            'token': os.getenv('ZENDESK_TOKEN'),
            'subdomain': os.getenv('ZENDESK_SUBDOMAIN')
        }
        self.zenpy_client = Zenpy(**creds)
        
        # --- Groq API Client Initialization for Classification ---
        GROQ_API_KEY = os.getenv('GROQ_API_KEY')
        self.groq_client = None
        if GROQ_API_KEY:
            try:
                self.groq_client = Groq(api_key=GROQ_API_KEY)
                print("✅ Groq client initialized successfully.")
            except Exception as e:
                print(f"❌ Failed to initialize Groq client: {e}")
        else:
            print("⚠️ GROQ_API_KEY not found in environment variables. Classification will not be available.")

    def classify_ticket_description(self, description: str):
        """
        Classifies a ticket description using the Groq API.
        Returns Department and Priority.
        """
        if not self.groq_client:
            return {"Department": "Unknown", "Priority": "Unknown", "error": "Groq client not loaded."}

        try:
            completion = self.groq_client.chat.completions.create(
                model="llama3-8b-8192",
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

    def search_user(self, email):
        users = list(self.zenpy_client.users.search(f"email:{email}"))
        if users:
            print(f"User with email '{email}' found.")
            return users[0]
        return None

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

        priority = "normal"
        department = "IT Support"

        if self.groq_client:
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
        else:
            print("Classification model not available. Using default values.")

        if customer:
            ticket = Ticket(
                subject=ticket_subject,
                description=ticket_description,
                requester_id=customer.id,
                assignee_id=assignee.id if assignee else None,
                priority=priority
            )
            created_ticket = self.zenpy_client.tickets.create(ticket)
            print(f"Ticket created successfully with ID: {created_ticket.ticket.id}")
            return created_ticket
        else:
            print("Could not create ticket. Customer not found or created.")
            return None

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
    zendesk = ZendeskIntegration()

    while True:
        print("\n--- Zendesk Ticket Management ---")
        print("1. Create a new ticket")
        print("2. View tickets")
        print("3. View users")
        print("4. Exit")
        choice = input("Enter your choice (1-4): ").strip()

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
            print("Exiting.")
            break
        else:
            print("Invalid choice. Please enter a number between 1 and 4.")