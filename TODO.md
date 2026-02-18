# TODO: Implement New Payload Format and Celery Task Structure

## Phase 1: Update Schemas - COMPLETED
- [x] 1.1 Update `audit/schemas/activity.py` - Add new `AuditLogsPayload` schema
- [x] 1.2 Update `audit/schemas/__init__.py` - Export new schema

## Phase 2: Update Validation Service - COMPLETED
- [x] 2.1 Update `audit/services/validation_service.py` - Handle new wrapped format

## Phase 3: Update Activity Interactor - COMPLETED
- [x] 3.1 Update `audit/interactors/activity_interactor.py` - Support both formats

## Phase 4: Create Message Model - COMPLETED
- [x] 4.1 Create `audit/models/message.py` - Message model inheriting from CoreMessageModel
- [x] 4.2 Create `audit/models/audit_history.py` - Move AuditHistory to models package
- [x] 4.3 Update `audit/models/__init__.py` - Export models

## Phase 5: Create Celery Configuration - COMPLETED
- [x] 5.1 Create `audit/enums.py` - Task name and queue enums
- [x] 5.2 Create `audit/config.py` - Celery app configuration

## Phase 6: Update Celery Tasks - COMPLETED
- [x] 6.1 Update `audit/tasks.py` - Refactor to follow new Celery pattern

## Phase 7: Update Views - COMPLETED
- [x] 7.1 Update `audit/views.py` - Handle new payload format

## Phase 8: Testing - COMPLETED
- [x] 8.1 Update `auditHistory/test_payload.json` - New format example

