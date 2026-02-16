# Audit History Service

## Enterprise Audit Logging System

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11+-blue?style=flat-square&logo=python" alt="Python">
  <img src="https://img.shields.io/badge/Django-4.2+-green?style=flat-square&logo=django" alt="Django">
  <img src="https://img.shields.io/badge/Celery-5.3+-orange?style=flat-square&logo=celery" alt="Celery">
  <img src="https://img.shields.io/badge/Redis-red?style=flat-square&logo=redis" alt="Redis">
  <img src="https://img.shields.io/badge/License-Proprietary-green?style=flat-square" alt="License">
</p>

---

## Table of Contents

1. [Overview](#overview)
2. [Business Value](#business-value)
3. [Features](#features)
4. [Architecture](#architecture)
5. [System Design](#system-design)
6. [Data Flow](#data-flow)
7. [API Reference](#api-reference)
8. [Payload Formats](#payload-formats)
9. [Project Structure](#project-structure)
10. [Services Overview](#services-overview)
11. [Interactors Overview](#interactors-overview)
12. [Installation](#installation)
13. [Running the Application](#running-the-application)
14. [Configuration](#configuration)
15. [Security Considerations](#security-considerations)
16. [Troubleshooting](#troubleshooting)
17. [Maintenance](#maintenance)

---

## Overview

**Audit History Service** is an enterprise-grade audit logging system built with Django and Django REST Framework. It provides comprehensive tracking of resource changes across your application, enabling compliance, security monitoring, and historical data analysis.

The system captures every create, update, and delete operation on resources, storing detailed change histories with automatic versioning, diff computation, and human-readable summaries.

---

## Business Value

| Benefit | Description |
|---------|-------------|
| **Compliance** | Meet regulatory requirements (GDPR, SOX, HIPAA) with complete audit trails |
| **Security** | Track unauthorized changes and investigate security incidents |
| **Accountability** | Assign every change to a specific actor with full attribution |
| **Troubleshooting** | Reconstruct historical states and diagnose issues |
| **Analytics** | Analyze change patterns and user behavior |
| **Recovery** | Roll back to previous states when needed |

---

## Features

### Core Features
- ✅ **Real-time Audit Logging** - Captures all resource changes instantly
- ✅ **Automatic Versioning** - Each resource maintains a complete version history
- ✅ **Change Diff Computation** - Shows exactly what changed between versions
- ✅ **Summary Generation** - Human-readable descriptions of changes
- ✅ **Actor Tracking** - Records who made each change
- ✅ **Multiple Payload Formats** - Supports Object, Resource, and Flat formats

### Technical Features
- ✅ **Async Processing** - Celery-based task queue for non-blocking operations
- ✅ **Pydantic Validation** - Type-safe payload validation
- ✅ **Modular Architecture** - Clean separation of concerns
- ✅ **RESTful API** - Easy integration with existing systems
- ✅ **Database Agnostic** - Works with any Django-supported database

---

## Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              CLIENT APPLICATIONS                             │
│  (Web App, Mobile App, Microservices, External Systems)                   │
└─────────────────────────────────┬───────────────────────────────────────────┘
                                  │ HTTP/JSON
                                  ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│                        Django REST Framework                                 │
│                          (API Layer)                                        │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────────────┐  │
│  │  ActivityViewSet │  │  Celery Worker   │  │  Management Commands    │  │
│  └────────┬────────┘  └────────┬────────┘  └────────────┬────────────┘  │
└───────────┼─────────────────────┼──────────────────────────┼───────────────┘
            │                     │                          │
            ↓                     ↓                          ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│                      INTERACTOR LAYER (Orchestration)                       │
│                                                                             │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                    ActivityInteractor                                │  │
│  │              (Main Orchestrator - Coordinates Flow)                │  │
│  └──────────┬─────────────────┬─────────────────┬────────────────────┘  │
│             │                 │                 │                        │
│  ┌──────────┴─────┐ ┌────────┴─────┐ ┌────────┴──────┐                 │
│  │ PayloadValidator│ │ActorExtractor│ │ResourceExtractor│              │
│  └────────┬─────┘ └────────┬─────┘ └────────┬──────┘                 │
└───────────┼─────────────────┼─────────────────┼─────────────────────────┘
            │                 │                 │
            ↓                 ↓                 ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│                        SERVICE LAYER (Business Logic)                       │
│                                                                             │
│  ┌────────────────┐  ┌──────────────┐  ┌───────────────┐  ┌────────────┐  │
│  │ValidationService│  │ ActorService │  │ResourceService│  │ResponseService│ │
│  └───────┬────────┘  └──────┬───────┘  └───────┬───────┘  └──────┬─────┘  │
│          │                  │                   │                  │        │
│  ┌───────┴──────────────────┴───────────────────┴──────────────────┴────┐ │
│  │                           AuditService                                 │ │
│  │              (compute_diff, generate_summary, verb_map)               │ │
│  └────────────────────────────────────┬────────────────────────────────────┘ │
└───────────────────────────────────────┼──────────────────────────────────────┘
                                        │
                                        ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│                      DATA LAYER (Persistence)                              │
│                                                                             │
│  ┌─────────────────────────┐              ┌─────────────────────────────┐ │
│  │    PostgreSQL/MySQL     │              │         Redis               │ │
│  │    (AuditHistory)       │              │    (Celery Broker)          │ │
│  └─────────────────────────┘              └─────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Design Patterns

| Pattern | Implementation |
|---------|----------------|
| **Interactor** | Coordinates business logic flow between services |
| **Service Layer** | Contains all business logic (validation, extraction, processing) |
| **Factory** | Pydantic schemas for different payload types |
| **Repository** | HistoryService for database operations |

---

## System Design

### Key Components

#### 1. API Layer (`views.py`)
- Accepts HTTP requests
- Handles authentication/authorization
- Returns formatted JSON responses

#### 2. Interactor Layer (`interactors/`)
- **Orchestration Only** - Coordinates flow between services
- No business logic - delegates to services
- Maintains single entry point for processing

#### 3. Service Layer (`services/`)
- **Business Logic** - All core functionality
- Stateless and testable
- No Django/ORM dependencies (except history_service)

#### 4. Data Layer (`models.py`)
- Django ORM models
- AuditHistory table for persistent storage

---

## Data Flow

### Processing Pipeline

```
┌─────────────┐
│   PAYLOAD   │  ← Input: Single dict or list of activity objects
└──────┬──────┘
       │
       ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│  STEP 1: VALIDATION                                                         │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ ValidationService.validate(payload)                                 │   │
│  │   • Validates using Pydantic schemas                               │   │
│  │   • Determines payload type (object/resource/flat)                │   │
│  │   • Returns: (validated_obj, payload_type)                        │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
       │
       ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│  STEP 2: ACTOR EXTRACTION                                                   │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ ActorService.extract_actor(payload, validated, payload_type)      │   │
│  │   • Extracts actor (user) information                              │   │
│  │   • Handles multiple payload formats                               │   │
│  │   • Returns: (actor_full, actor_id)                               │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
       │
       ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│  STEP 3: RESOURCE EXTRACTION                                               │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ ResourceService.extract_resource(payload, validated, payload_type)  │   │
│  │   • Extracts resource information (id, type, data)                 │   │
│  │   • Filters metadata fields                                        │   │
│  │   • Returns: (res_id, res_type, data)                             │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
       │
       ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│  STEP 4: VERB MAPPING                                                       │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ audit_service.verb_map                                             │   │
│  │   • Maps action verbs to operations                                │   │
│  │   • "create" → "created", "update" → "updated", etc.              │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
       │
       ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│  STEP 5: HISTORY RETRIEVAL                                                  │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ HistoryService.get_last_history(res_type, res_id)                  │   │
│  │   • Gets previous version of resource                              │   │
│  │   • Returns: AuditHistory or None                                  │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
       │
       ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│  STEP 6: DIFF COMPUTATION                                                   │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ audit_service.compute_diff(old_data, new_data)                     │   │
│  │   • Computes changes between old and new states                    │   │
│  │   • Uses DeepDiff for accurate comparison                          │   │
│  │   • Returns: changes dict {field: [old_value, new_value]}         │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
       │
       ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│  STEP 7: SUMMARY GENERATION                                                 │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ audit_service.generate_summary(changes)                            │   │
│  │   • Creates human-readable description                             │   │
│  │   • Returns: summary string                                        │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
       │
       ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│  STEP 8: PERSISTENCE                                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ HistoryService.create_history(...)                                  │   │
│  │   • Saves AuditHistory record                                      │   │
│  │   • Auto-increments version                                        │   │
│  │   • Stores all changes and metadata                                │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
       │
       ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│  STEP 9: RESPONSE BUILDING                                                  │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ ResponseService.build_response(...)                                │   │
│  │   • Builds standardized API response                               │   │
│  │   • Returns: response dict                                          │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
       │
       ↓
┌─────────────┐
│   RESPONSE  │  ← Output: List of audit records
└─────────────┘
```

---

## API Reference

### Endpoint

```
POST /api/v1/audit/activity-stream/
```

### Authentication

All endpoints require authentication via one of:
- API Key (`Authorization: ApiKey <key>`)
- JWT Token (`Authorization: Bearer <token>`)
- Session Cookie (for browser clients)

### Headers

| Header | Required | Description |
|--------|----------|-------------|
| `Content-Type` | Yes | Must be `application/json` |
| `Authorization` | Yes | Authentication credentials |
| `X-Request-ID` | No | Request correlation ID |

### Request Body

**Single Activity:**
```json
{
  "actor": {"id": "user_123", "name": "John Doe"},
  "verb": "create",
  "object": {
    "id": "resource_456",
    "type": "user",
    "name": "New User",
    "email": "user@example.com"
  }
}
```

**Multiple Activities (Batch):**
```json
[
  {
    "actor": {"id": "user_123", "name": "John Doe"},
    "verb": "create",
    "object": {"id": "res_1", "type": "user", "name": "User 1"}
  },
  {
    "actor": {"id": "user_456", "name": "Jane Smith"},
    "verb": "update",
    "object": {"id": "res_2", "type": "document", "title": "Updated Doc"}
  }
]
```

### Response

```json
{
  "status": "success",
  "data": [
    {
      "id": "uuid-of-audit-record",
      "actor": {"id": "user_123", "name": "John Doe"},
      "verb": "created",
      "object": {
        "id": "resource_456",
        "type": "user",
        "fields": {
          "name": [null, "New User"],
          "email": [null, "user@example.com"]
        }
      },
      "description": "Name set to New User and email set to user@example.com.",
      "created_at": "2026-02-16T11:31:39.762704+00:00",
      "updated_at": "2026-02-16T11:31:39.762704+00:00"
    }
  ],
  "metadata": {
    "processed_count": 1,
    "timestamp": "2026-02-16T11:31:39.762704+00:00"
  }
}
```

### Response Codes

| Code | Description |
|------|-------------|
| `200` | Success |
| `400` | Bad Request - Invalid payload format |
| `401` | Unauthorized - Invalid authentication |
| `403` | Forbidden - Insufficient permissions |
| `422` | Unprocessable Entity - Validation error |
| `500` | Internal Server Error |

---

## Payload Formats

### Format 1: Object Style

Recommended for most use cases with structured objects.

```json
{
  "actor": {
    "id": "user_123",
    "name": "John Doe",
    "email": "john@company.com"
  },
  "verb": "create",
  "object": {
    "id": "order_456",
    "type": "order",
    "customer": "Acme Corp",
    "amount": 1500.00,
    "status": "pending"
  }
}
```

### Format 2: Resource Style

For RESTful resource representations.

```json
{
  "actor": {
    "id": "user_123",
    "name": "John Doe"
  },
  "verb": "update",
  "resource": {
    "id": "invoice_789",
    "type": "invoice",
    "data": {
      "status": "paid",
      "paid_date": "2026-02-16"
    }
  }
}
```

### Format 3: Flat Style

For simple, flat data structures.

```json
{
  "actor_id": "user_123",
  "verb": "delete",
  "id": "record_999",
  "type": "transaction",
  "reason": "Duplicate entry"
}
```

### Verb Mapping

| Input Verb | Mapped Operation |
|------------|------------------|
| `create`, `created`, `add` | `created` |
| `update`, `updated`, `edit`, `change` | `updated` |
| `delete`, `deleted`, `remove` | `deleted` |

---

## Project Structure

```
audit-history/
│
├── audit/                           # Main Django app
│   │
│   ├── interactors/                # Orchestration layer
│   │   ├── __init__.py
│   │   ├── activity_interactor.py  # Main orchestrator
│   │   ├── payload_validator.py    # Wrapper → ValidationService
│   │   ├── actor_extractor.py      # Wrapper → ActorService
│   │   ├── resource_extractor.py   # Wrapper → ResourceService
│   │   └── response_builder.py     # Wrapper → ResponseService
│   │
│   ├── services/                   # Business logic layer
│   │   ├── __init__.py
│   │   ├── audit_service.py       # Diff computation, summaries
│   │   ├── validation_service.py  # Payload validation
│   │   ├── actor_service.py       # Actor extraction
│   │   ├── resource_service.py    # Resource extraction
│   │   ├── history_service.py     # Database operations
│   │   └── response_service.py    # Response building
│   │
│   ├── schemas/                    # Pydantic models
│   │   ├── __init__.py
│   │   ├── activity.py
│   │   ├── actor.py
│   │   └── resource.py
│   │
│   ├── migrations/                 # Database migrations
│   ├── models.py                   # Django models (AuditHistory)
│   ├── views.py                    # API views
│   ├── urls.py                     # URL routing
│   ├── tasks.py                    # Celery tasks
│   ├── admin.py                    # Django admin
│   └── tests.py                    # Unit tests
│
├── auditHistory/                   # Django project settings
│   ├── __init__.py
│   ├── settings.py                 # Project configuration
│   ├── urls.py                     # Root URL configuration
│   ├── celery.py                   # Celery configuration
│   ├── asgi.py
│   └── wsgi.py
│
├── audit/management/               # Management commands
│   └── commands/
│       └── process_activity.py
│
├── manage.py                       # Django management script
├── requirements.txt                # Python dependencies
├── README.md                       # This file
└── .env.example                    # Environment variables template
```

---

## Services Overview

| Service | File | Responsibility |
|---------|------|----------------|
| **ValidationService** | `validation_service.py` | Validates payloads using Pydantic models |
| **ActorService** | `actor_service.py` | Extracts actor/user information |
| **ResourceService** | `resource_service.py` | Extracts resource/object information |
| **HistoryService** | `history_service.py` | Database CRUD for AuditHistory |
| **ResponseService** | `response_service.py` | Builds standardized API responses |
| **AuditService** | `audit_service.py` | compute_diff, generate_summary, verb_map |

---

## Interactors Overview

| Interactor | File | Purpose |
|------------|------|---------|
| **ActivityInteractor** | `activity_interactor.py` | Main orchestrator - coordinates flow |
| **PayloadValidator** | `payload_validator.py` | Delegates to ValidationService |
| **ActorExtractor** | `actor_extractor.py` | Delegates to ActorService |
| **ResourceExtractor** | `resource_extractor.py` | Delegates to ResourceService |
| **ResponseBuilder** | `response_builder.py` | Delegates to ResponseService |

---

## Installation

### Prerequisites

- Python 3.11+
- PostgreSQL 14+ or MySQL 8.0+
- Redis 6.0+
- Celery 5.3+

### Step 1: Clone and Setup

```bash
# Clone the repository
git clon https://github.com/Shivam-ye/audit.git 
cd audit-history

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Environment Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your settings
# See Configuration section below
```

### Step 4: Database Setup

```bash
# Run migrations
python manage.py migrate

# Create superuser (optional)
python manage.py createsuperuser
```

### Step 5: Start Services

```bash
# Start Redis (if not running)
redis-server

# Start Celery worker
celery -A auditHistory worker -l info -c 4

# Start Celery beat (if using scheduled tasks)
celery -A auditHistory beat -l info
```

### Step 6: Run Django Server

```bash
python manage.py runserver 0.0.0.0:9002
```

---

## Running the Application

### Development Mode

```bash
# Terminal 1: Django server
python manage.py runserver 9002

# Terminal 2: Celery worker
celery -A auditHistory worker -l info
```

### Production Mode

```bash
# Using Gunicorn
gunicorn auditHistory.wsgi:application --bind 0.0.0.0:9002 --workers 4

# Celery workers (multiple)
celery -A auditHistory worker -l info -c 4 -Q audit_log_queue
celery -A auditHistory worker -l info -c 2 -Q high_priority
```

### Management Commands

```bash
# Process activities from JSON file
python manage.py process_activity --file path/to/payload.json

# Process activities with custom queue
python manage.py process_activity --file path/to/payload.json --queue high_priority

# View audit history
python manage.py show_audit --resource-type user --resource-id 123

# Cleanup old records (use with caution)
python manage.py cleanup_audit --days 365 --dry-run
```

---

## Configuration

### Environment Variables (.env)

```bash
# Django Settings
DEBUG=False
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DATABASE_ENGINE=django.db.backends.postgresql
DATABASE_NAME=audit_db
DATABASE_USER=audit_user
DATABASE_PASSWORD=secure_password
DATABASE_HOST=localhost
DATABASE_PORT=5432

# Redis
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Celery
CELERY_TASK_TRACK_STARTED=True
CELERY_TASK_TIME_LIMIT=3600

# Logging
LOG_LEVEL=INFO
LOG_FILE=/var/log/audit/app.log
```

### Django Settings (settings.py)

Key settings for audit service:

```python
# Celery Configuration
CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0')
CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'audit': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}
```

---

## Security Considerations

### Authentication & Authorization

1. **API Keys** - Use for service-to-service communication
2. **JWT Tokens** - Use for user authentication
3. **IP Whitelisting** - Restrict access by IP in production

### Data Security

1. **Encrypt at Rest** - Enable database encryption
2. **Encrypt in Transit** - Use TLS/SSL
3. **Redact Sensitive Data** - Never log passwords, tokens, PII

### Audit Trail Integrity

1. **Immutable Records** - Audit records should never be modified
2. **Tamper Detection** - Consider adding digital signatures
3. **Backup Strategy** - Regular backups with retention policy

### Example: Redacting Sensitive Fields

```python
# In resource_service.py
SENSITIVE_FIELDS = {'password', 'token', 'secret', 'api_key'}

def extract_resource(payload, validated, payload_type):
    # ... extraction logic ...
    
    # Redact sensitive fields
    for field in SENSITIVE_FIELDS:
        if field in data:
            data[field] = '[REDACTED]'
    
    return res_id, res_type, data
```

---

## Troubleshooting

### Common Issues

#### 1. Celery Connection Refused

```bash
# Check if Redis is running
redis-cli ping

# Start Redis
redis-server
```

#### 2. Database Connection Error

```bash
# Check database credentials
python manage.py dbshell

# Run migrations
python manage.py migrate
```

#### 3. Empty Changes in Response

Check logs for debug information:
```bash
celery -A auditHistory worker -l DEBUG
```

Ensure payload contains the data:
```json
{
  "object": {
    "id": "123",
    "type": "user",
    "name": "John"  // This field should be captured
  }
}
```

#### 4. Validation Errors

Verify payload matches expected format:
```json
// Object style requires "object" with "id" and "type"
{
  "verb": "create",
  "actor": {"id": "1"},
  "object": {
    "id": "123",
    "type": "user",
    "data": "..."
  }
}
```

### Debug Mode

Enable debug logging:

```bash
# Set log level to DEBUG
export LOG_LEVEL=DEBUG

# Or in settings.py
LOGGING['loggers']['audit']['level'] = 'DEBUG'
```

### Health Check

```bash
# Check Django health
curl http://localhost:9002/health/

# Check Celery health
celery -A auditHistory inspect ping
```

---

## Maintenance

### Database Maintenance

```bash
# Create migration
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Show migration status
python manage.py showmigrations
```

### Monitoring

```bash
# Celery events
celery -A auditHistory events

# Flower monitoring (install flower first)
pip install flower
celery -A auditHistory flower --port=5555
```

### Backup & Recovery

```bash
# Backup database
pg_dump audit_db > backup_$(date +%Y%m%d).sql

# Restore database
psql audit_db < backup_20260216.sql
```

---

## Performance Optimization

### Tips

1. **Indexing** - Add database indexes on frequently queried fields:
   - `resource_type`
   - `resource_id`
   - `timestamp`
   - `actor_id`

2. **Batch Processing** - Send multiple activities in a single request:
   ```json
   [
     {"object": {"id": "1", "type": "user", ...}},
     {"object": {"id": "2", "type": "user", ...}},
     {"object": {"id": "3", "type": "user", ...}}
   ]
   ```

3. **Async Processing** - Use Celery for high-volume scenarios

4. **Connection Pooling** - Configure database connection pooling

---

## Support & Contact

For issues, questions, or contributions:

- **Technical Lead**: [Name]
- **Email**: [email@company.com]
- **Slack**: #audit-system

---

## License

Proprietary - All rights reserved © 2026 [Company Name]

---

## Appendix: Database Schema

### AuditHistory Model

| Field | Type | Description |
|-------|------|-------------|
| `id` | UUID | Primary key |
| `resource_type` | String(100) | Type of resource (user, order, etc.) |
| `resource_id` | String(255) | Unique identifier of resource |
| `version` | Integer | Auto-incrementing version number |
| `operation` | String(20) | created, updated, deleted |
| `actor` | JSON | Actor details |
| `actor_id` | String(255) | Actor identifier |
| `changes` | JSON | Field-level changes |
| `summary` | Text | Human-readable summary |
| `full_fields_after` | JSON | Complete state after change |
| `timestamp` | DateTime | When the change occurred |

### Indexes

```sql
CREATE INDEX idx_resource ON audit_history(resource_type, resource_id);
CREATE INDEX idx_timestamp ON audit_history(timestamp);
CREATE INDEX idx_actor ON audit_history(actor_id);
```

---

*Last Updated: February 2026*
*Version: 1.0.0*

