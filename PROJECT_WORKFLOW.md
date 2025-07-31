# RouteIQ Project Workflow

This document explains the step-by-step workflow of the RouteIQ project, focusing on how ticket classification and routing works.

## Project Overview

RouteIQ is a ticket management system that automatically classifies and routes support tickets to the appropriate departments using machine learning. The system supports integration with multiple ticket management platforms including Zammad and Zendesk.

## Project Components

### 1. Machine Learning Classifier

**Location**: `backend/Dataset/ticket_classifier/`

This is a FastAPI service that provides ticket classification capabilities:

- **Models**: Pre-trained ML models stored as pickle files in `backend/Dataset/models/`
  - TF-IDF Vectorizer (`tfidf_vectorizer.pkl`)
  - Label Encoders for department and priority (`le_department.pkl`, `le_priority.pkl`)
  - Logistic Regression models for department and priority prediction (`log_reg_dept_model.pkl`, `log_reg_prio_model.pkl`)

- **API Endpoints**:
  - Health check: `GET /api/v1/health`
  - Prediction: `POST /api/v1/predict`

- **Classification Process**:
  1. Text preprocessing (cleaning, lowercasing, stop word removal, lemmatization)
  2. Feature extraction using TF-IDF vectorizer
  3. Prediction using logistic regression models
  4. Return predicted department and priority

### 2. Zammad Integration

**Location**: `backend/zammad/`

Handles integration with the Zammad ticketing system:

- **zammad_api.py**: Provides a high-level API for ticket creation with automatic classification
- **zammad_integration.py**: Contains lower-level functions for interacting with the Zammad API

### 3. Zendesk Integration

**Location**: `backend/zendesk/`

Handles integration with the Zendesk ticketing system:

- **zendesk_integration.py**: Provides functionality for ticket creation and management in Zendesk

## Workflow Steps

### Ticket Classification and Creation in Zammad

1. **Ticket Submission**:
   - A user submits a ticket with a title, description, and customer information
   - The ticket data is received by the `create_ticket` function in `zammad_api.py`

2. **Customer Management**:
   - The system checks if the customer exists in Zammad
   - If not, a new customer is created using `find_or_create_customer` from `zammad_integration.py`

3. **Group Assignment**:
   - If a specific group (department) is provided, the ticket is assigned to that group
   - If no group is specified, automatic classification is triggered

4. **Automatic Classification** (when no group is specified):
   - The `predict_ticket_category` function in `zammad_api.py` is called
   - This function sends a POST request to the FastAPI classifier service at `http://127.0.0.1:8000/api/v1/predict`
   - The request includes the ticket description
   - The classifier service processes the description and returns the predicted department and priority

5. **Group Resolution**:
   - The system checks if the predicted department exists in the available Zammad groups
   - If it exists, the ticket is assigned to that group
   - If not, it defaults to the first available group or group ID 1

6. **Ticket Creation**:
   - The ticket is created in Zammad with the determined customer ID, group ID, and other parameters
   - The API returns the created ticket information or an error message

### Running the System

1. **Start the Classifier Service**:
   ```bash
   cd backend/Dataset/ticket_classifier
   python -m uvicorn ticket_classifier.app.main:app --reload
   ```

2. **Use the Zammad API**:
   - Import and use the functions from `zammad_api.py` to create tickets with automatic classification

## Data Flow Diagram

```
+----------------+     +-------------------+     +----------------------+
|                |     |                   |     |                      |
| Ticket Request |---->| zammad_api.py    |---->| Zammad API          |
|                |     | (create_ticket)   |     | (Ticket Creation)   |
+----------------+     +-------------------+     +----------------------+
                              |                             ^
                              | (if no group specified)      |
                              v                             |
                       +-------------------+                |
                       |                   |                |
                       | FastAPI Classifier|                |
                       | Service           |----------------+
                       |                   |   (assign group based
                       +-------------------+    on prediction)
                              |
                              v
                       +---------------------------+
                       |                           |
                       | ML Models                 |
                       | (for now                  |
                       |           Logistic        |
                       |  Regression)              |
                       +---------------------------+
```

## Key Files and Their Roles

- **zammad_api.py**: High-level API for ticket creation with automatic classification
- **zammad_integration.py**: Low-level functions for Zammad API interaction
- **ticket_classifier/app/main.py**: FastAPI application setup
- **ticket_classifier/app/api/endpoints.py**: API route definitions
- **ticket_classifier/app/services/classifier_service.py**: ML model loading and prediction logic
- **ticket_classifier/app/models/schemas.py**: Request and response data models

## Configuration

- **ticket_classifier/config.py**: Defines paths to ML models and API settings
- Environment variables for API credentials are loaded from `.env` files

This document provides a comprehensive overview of how the RouteIQ project works, focusing on the ticket classification and routing workflow.