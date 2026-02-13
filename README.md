# Audit History Service

A modular **Django + DRF** based audit logging service that tracks resource changes using structured activity payloads.

This service validates activity data using **Pydantic**, processes business logic through **Interactors**, and stores audit records in the database.

## Features

- Activity stream endpoint (`POST /audit/activity-stream/`)
- Supports multiple payload formats:
  - Object style
  - Resource style
  - Flat style
- Pydantic-based validation
- Modular architecture (Interactor pattern)
- Automatic versioning of resources
- Change diff computation
- Summary generation
- DRF ViewSet-based API
- Fully testable structure

## Project Structure
```
audit/
│
├── interactors/                    # Business logic layer (Interactor pattern)
│   ├── activity_interactor.py
│   ├── payload_validator.py
│   ├── actor_extractor.py
│   ├── resource_extractor.py
│   └── response_builder.py
│
├── schemas/                        # Pydantic models / validation schemas
│   ├── activity.py
│   ├── actor.py
│   └── resource.py
│
├── services/                       # Pure functions, no Django/ORM dependency
│   └── audit_service.py
│
├── models.py                       # Django model: AuditHistory
├── views.py                        # DRF ViewSet(s)
├── urls.py                         # API routes
└── tests.py                        # Unit/integration tests
```


## Architecture Overview

1. **View** (`views.py`)
   - Accepts HTTP request
   - Parses JSON
   - Calls `ActivityInteractor`
   - Returns formatted response  
   → The view remains **thin and clean**.

2. **Interactors** (Business Logic Layer)  
   The `ActivityInteractor` coordinates the process:

   1. Validate payload (Pydantic schemas)
   2. Extract actor information
   3. Extract resource information
   4. Compute diff
   5. Generate summary
   6. Save audit record
   7. Build response

   Each responsibility is separated into its own module.

3. **Schemas** (Validation Layer)  
   Uses **Pydantic** for:
   - Field validation
   - Type enforcement
   - Alias handling
   - Nested object parsing

   Supported payload types:
   - `ActivityWithObject`
   - `ActivityWithResource`
   - `FlatActivity`

   If validation fails → returns **HTTP 422**.

4. **Services**  
   `audit_service.py` contains pure functions (no Django dependencies):

   - `compute_diff(old, new)`
   - `generate_summary(changes)`
   - `verb_map`

##  Installation

1. Clone repository

   ```bash
   git clone <repo-url>
   cd audit-history
   ```

2. Create virtual environment 
    ```
    python -m venv venv
    source venv/bin/activate
    ```

3. Install dependencies
    ```
    pip install -r requirements.txt
    ```
4. Apply migrations 
    ```
    python manage.py migrate
    ```

5. Run server
    ```
    python manage.py runserver
    ```

API Endpoint
``` POST /audit/activity-stream/ ```
Accepts:

Single activity object
OR list of activity objects

Example (Object Style)
```
{
  "actor": {
    "id": "",
    "name": "",
    "so-on"
  },
  "verb": "update/delete/create...",
  "object": {
    "id": "",
    "type": "",
    "more data"
  }
}
```
Example Response
```
[
  {
    "id": "uuid",
    "actor": {
      "id": "",
      "name":"",
      "so-on"
    },
    "verb": "updated",
    "object": {
      "id": "",
      "type": "",
      "fields": {
        "changed": {
          [ "old", "new"]
        },
        more changes...
      }
    },
    "description": "Updated from -> to ",
    "created_at": "exact time"
  }
]
```

Design Principles

- Thin views
- Business logic separated from HTTP layer
- Single Responsibility Principle
- Modular folder structure
- Clear separation of concerns:

    - Validation
    - Extraction
    - Processing
    - Persistence
    - Response building


Notes

- Currently using Django development server
- Not configured for production deployment
- Use proper WSGI/ASGI server (gunicorn + uvicorn, etc.) in production
