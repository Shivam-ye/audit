# Audit History Service

A modular **Django + DRF** based audit logging service that tracks resource changes using structured activity payloads.

This service validates activity data using **Pydantic**, processes business logic through **Services**, and stores audit records in the database.

## Features

- Activity stream endpoint (`POST /audit/activity-stream/`)
- Supports multiple payload formats:
  - Object style
  - Resource style
  - Flat style
- Pydantic-based validation
- Modular architecture (Service Layer pattern)
- Automatic versioning of resources
- Change diff computation
- Summary generation
- DRF ViewSet-based API
- Fully testable structure

## Project Structure

```
audit/
│
├── interactors/                    # Orchestration layer (coordinates flow)
│   ├── activity_interactor.py      # Main orchestrator
│   ├── payload_validator.py        # Thin wrapper → ValidationService
│   ├── actor_extractor.py          # Thin wrapper → ActorService
│   ├── resource_extractor.py       # Thin wrapper → ResourceService
│   └── response_builder.py         # Thin wrapper → ResponseService
│
├── services/                       # Business logic layer
│   ├── audit_service.py            # Diff computation, summary generation, verb mapping
│   ├── validation_service.py       # Payload validation (Pydantic)
│   ├── actor_service.py            # Actor extraction logic
│   ├── resource_service.py         # Resource extraction logic
│   ├── history_service.py          # Database operations (AuditHistory CRUD)
│   └── response_service.py         # Response building logic
│
├── schemas/                        # Pydantic models / validation schemas
│   ├── activity.py
│   ├── actor.py
│   └── resource.py
│
├── models.py                       # Django model: AuditHistory
├── views.py                        # DRF ViewSet(s)
├── urls.py                         # API routes
├── tasks.py                        # Celery tasks
└── tests.py                        # Unit/integration tests
```

## Architecture Overview

### Layered Architecture:

```
┌─────────────────────────────────────────┐
│           Views / Tasks                 │  ← Entry Points
└─────────────────┬───────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│         Interactors (Orchestration)    │  ← Coordinates flow
│    activity_interactor.py               │
└─────────────────┬───────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│           Services (Business Logic)    │  ← Core logic
│  validation_service.py                  │
│  actor_service.py                       │
│  resource_service.py                    │
│  history_service.py                    │
│  response_service.py                    │
│  audit_service.py                       │
└─────────────────┬───────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│             Models / DB                 │  ← Persistence
│          AuditHistory                    │
└─────────────────────────────────────────┘
```

## Data Flow

### Step-by-Step Processing Flow:

```
1. Input: payloads (dict or list)
    ↓
2. activity_interactor.py (Orchestrator)
    ↓
3. validation_service.py
   - Validates payload using Pydantic
   - Returns: (validated_obj, payload_type)
    ↓
4. actor_service.py  
   - Extracts actor info from validated payload
   - Returns: (actor_full, actor_id)
    ↓
5. resource_service.py
   - Extracts resource info (id, type, data)
   - Returns: (res_id, res_type, data)
    ↓
6. audit_service.py (verb_map)
   - Maps verb (e.g., "create" → "created")
    ↓
7. history_service.py
   - Gets last AuditHistory record
   - Returns: last or None
    ↓
8. audit_service.py (compute_diff)
   - Computes changes between old & new data
   - Returns: changes dict
    ↓
9. audit_service.py (generate_summary)
   - Generates human-readable summary
   - Returns: summary string
    ↓
10. history_service.py
    - Creates new AuditHistory record in DB
    ↓
11. response_service.py
    - Builds final API response
    ↓
12. Return result to caller
```

## Services Description

| Service | Purpose |
|---------|---------|
| **validation_service.py** | Validates incoming payloads using Pydantic models (FlatActivity, ActivityWithObject, ActivityWithResource) |
| **actor_service.py** | Extracts actor (user) information from various payload formats |
| **resource_service.py** | Extracts resource (object) information from various payload formats |
| **history_service.py** | Database CRUD operations for AuditHistory model |
| **response_service.py** | Builds standardized API response dictionary |
| **audit_service.py** | Pure functions: compute_diff(), generate_summary(), verb_map |

## Interactors Description

| Interactor | Purpose |
|------------|---------|
| **activity_interactor.py** | Main orchestrator - coordinates the flow between services |
| **payload_validator.py** | Thin wrapper - delegates to ValidationService |
| **actor_extractor.py** | Thin wrapper - delegates to ActorService |
| **resource_extractor.py** | Thin wrapper - delegates to ResourceService |
| **response_builder.py** | Thin wrapper - delegates to ResponseService |

## Supported Payload Types

### 1. Object Style
```json
{
  "actor": {"id": "12", "name": "John"},
  "verb": "create",
  "object": {
    "id": "user-1",
    "type": "user",
    "username": "johndoe",
    "email": "john@example.com"
  }
}
```

### 2. Resource Style
```json
{
  "actor": {"id": "12", "name": "John"},
  "verb": "update",
  "resource": {
    "id": "user-1",
    "type": "user",
    "data": {"username": "johndoe"}
  }
}
```

### 3. Flat Style
```json
{
  "actor_id": "12",
  "verb": "delete",
  "id": "user-1",
  "type": "user"
}
```

## API Endpoint

```
POST /audit/activity-stream/
```

### Example Request:
```json
{
  "actor": {"id": "12", "name": "shivam"},
  "verb": "create",
  "object": {
    "id": "user-451",
    "type": "user123",
    "username": "new user",
    "age": "21",
    "email": "shivam@example.com"
  }
}
```

### Example Response:
```json
[
  {
    "id": "uuid",
    "actor": {"id": "12", "name": "shivam"},
    "verb": "created",
    "object": {
      "id": "user-451",
      "type": "user123",
      "fields": {
        "username": [null, "new user"],
        "age": [null, "21"],
        "email": [null, "shivam@example.com"]
      }
    },
    "description": "Username set to new user, age set to 21, email set to shivam@example.com.",
    "created_at": "2026-02-16T11:31:39.762704+00:00",
    "updated_at": "2026-02-16T11:31:39.762704+00:00"
  }
]
```

## Installation

1. Clone repository
   ```bash
   git clone https://github.com/shivam-ye/audit
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

## Running the Application

### Run Django Server:
```
python manage.py runserver 9002
```

### Run Celery Worker:
```
celery -A auditHistory worker -l info
```

### Run Management Command:
```
python manage.py process_activity --file auditHistory/test_payload.json
```

## Design Principles

- **Thin Views** - Views only handle HTTP, no business logic
- **Orchestration in Interactors** - Coordinate flow between services
- **Business Logic in Services** - All core logic separated into services
- **Single Responsibility Principle** - Each service has one purpose
- **Modular Folder Structure** - Easy to maintain and test
- **Clear Separation of Concerns**:
  - Validation → validation_service.py
  - Actor Extraction → actor_service.py
  - Resource Extraction → resource_service.py
  - Database Operations → history_service.py
  - Response Building → response_service.py
  - Diff Computation → audit_service.py

## Notes

- Currently using Django development server
- Not configured for production deployment
- Use proper WSGI/ASGI server (gunicorn + uvicorn, etc.) in production
- Redis is required for Celery task queue

