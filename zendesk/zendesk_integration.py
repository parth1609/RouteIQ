
import os
import json
from dotenv import load_dotenv, find_dotenv
from zenpy import Zenpy
from zenpy.lib.api_objects import Ticket, User
from Model.evaluation import ITTicketEvaluator

class ZendeskIntegration:
    def __init__(self):
        load_dotenv()
        creds = {
            'email': os.getenv('ZENDESK_EMAIL'),
            'token': os.getenv('ZENDESK_TOKEN'),
            'subdomain': os.getenv('ZENDESK_SUBDOMAIN')
        }
        self.zenpy_client = Zenpy(**creds)
        model_id = os.getenv('HF_MODEL_ID')
        api_token = os.getenv('HF_TOKEN')
        self.ticket_evaluator = ITTicketEvaluator(model_id=model_id, api_token=api_token)

    def search_user(self, email):
        users = self.zenpy_client.users.search(f"email:{email}")
        user_list = list(users)
        if user_list:
            print(f"User with email '{email}' found.")
            return user_list[0]
        return None

    def create_user(self, email, name, role):
        print(f"Creating a new user with email '{email}'.")
        user = User(name=name, email=email, role=role)
        return self.zenpy_client.users.create(user)

    def create_ticket_with_classification(self, customer_email, customer_name, assignee_email, assignee_name, ticket_subject, ticket_description):
        """
        Creates a new ticket with automated classification of priority and department.

        Args:
            customer_email (str): The email of the customer (requester).
            customer_name (str): The name of the customer.
            assignee_email (str): The email of the assignee (agent).
            assignee_name (str): The name of the assignee.
            ticket_subject (str): The subject of the ticket.
            ticket_description (str): The description of the ticket.

        Returns:
            zenpy.lib.api_objects.Ticket or None: The created Ticket object or None if creation failed.
        """
        # Search for the customer by email
        customer = self.search_user(customer_email)
        # If the customer is not found, create a new one
        if not customer:
            customer = self.create_user(customer_email, customer_name, 'end-user')

        # Search for the assignee by email
        assignee = self.search_user(assignee_email)
        # If the assignee is not found, create a new one
        if not assignee:
            assignee = self.create_user(assignee_email, assignee_name, 'agent')

        # Classify the ticket description to determine priority and department
        classification_result = self.ticket_evaluator.classify_with_custom_classifier([ticket_description])
        
        # If classification fails, use default values
        if not classification_result or 'error' in classification_result[0]:
            print("Could not classify ticket. Creating ticket with default values.")
            priority = "normal"
            department = "IT Support"
        else:
            # Otherwise, use the classified priority and department
            priority = classification_result[0].get('priority', 'normal')
            department = classification_result[0].get('department', 'IT Support')
            # Print the generated information
            print(f"Generated Priority: {priority}")
            print(f"Generated Department: {department}")

            # Ask for user confirmation
            proceed = input("Proceed with this information? (yes/no): ").strip().lower()
            if proceed != 'yes':
                priority = input("Enter priority: ").strip()
                department = input("Enter department: ").strip()

        # If both customer and assignee exist, create the ticket
        if customer and assignee:
            ticket = Ticket(
                subject=ticket_subject,
                description=ticket_description,
                requester_id=customer.id,
                assignee_id=assignee.id,
                priority=priority
            )
            # Create the ticket in Zendesk
            created_ticket = self.zenpy_client.tickets.create(ticket)
            print(f"Ticket created successfully with ID: {created_ticket.ticket.id}")
            return created_ticket
        else:
            # If customer or assignee is missing, print an error message
            print("Could not create ticket. Customer or assignee not found or created.")
            return None

    def _print_ticket_details(self, ticket):
        """Helper function to print ticket details."""
        print(f"Ticket ID: {ticket.id}, Subject: {ticket.subject}, Status: {ticket.status}")
        if ticket.assignee_id:
            try:
                assignee = self.zenpy_client.users(id=ticket.assignee_id)
                print(f"  Assignee: {assignee.name}, Email: {assignee.email}")
            except Exception as e:
                print(f"  Could not retrieve assignee details for ID {ticket.assignee_id}: {e}")

        if ticket.requester_id:
            try:
                requester = self.zenpy_client.users(id=ticket.requester_id)
                print(f"  Requester: {requester.name}, Email: {requester.email}")
            except Exception as e:
                print(f"  Could not retrieve requester details for ID {ticket.requester_id}: {e}")
        print("-" * 20)

    def search_tickets(self, search_query):
        """
        Searches for tickets using a search query and prints the results.
        """
        if not search_query:
            print("Search query cannot be empty for a custom search.")
            return

        print(f"\nSearching for tickets with query: '{search_query}'")
        try:
            tickets = self.zenpy_client.search(search_query, type='ticket')
            results_found = False
            for ticket in tickets:
                results_found = True
                self._print_ticket_details(ticket)
            if not results_found:
                print("No tickets found matching your query.")
        except Exception as e:
            print(f"An error occurred while searching for tickets: {e}")

    def view_all_tickets(self):
        """
        Retrieves and prints all tickets.
        """
        print("\nRetrieving all tickets...")
        try:
            tickets = self.zenpy_client.tickets()
            results_found = False
            for ticket in tickets:
                results_found = True
                self._print_ticket_details(ticket)
            if not results_found:
                print("No tickets found.")
        except Exception as e:
            print(f"An error occurred while retrieving tickets: {e}")

    def view_all_customers(self):
        """
        Retrieves and prints all customers (end-users).
        """
        print("\nRetrieving all customers...")
        try:
            customers = self.zenpy_client.users(role="end-user")
            results_found = False
            for customer in customers:
                results_found = True
                print(f"  Customer: {customer.name}, Email: {customer.email}")
            if not results_found:
                print("No customers found.")
        except Exception as e:
            print(f"An error occurred while retrieving customers: {e}")

    def view_all_assignees(self):
        """
        Retrieves and prints all assignees (agents).
        """
        print("\nRetrieving all assignees...")
        try:
            agents = self.zenpy_client.users(role="agent")
            results_found = False
            for agent in agents:
                results_found = True
                print(f"  Assignee: {agent.name}, Email: {agent.email}")
            if not results_found:
                print("No assignees found.")
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

