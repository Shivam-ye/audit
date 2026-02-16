# Refactoring Plan: Move Business Logic from Interactors to Services

## Objective
Keep interactors for orchestration only, move all business logic to services.

## Steps to Complete:

### Step 1: Create new service files
- [x] 1. Create `validation_service.py` - move validation logic from PayloadValidator
- [x] 2. Create `actor_service.py` - move actor extraction logic from ActorExtractor
- [x] 3. Create `resource_service.py` - move resource extraction logic from ResourceExtractor
- [x] 4. Create `history_service.py` - move database operations (AuditHistory create/filter)
- [x] 5. Create `response_service.py` - move response building logic from ResponseBuilder

### Step 2: Refactor interactor files
- [x] 6. Refactor `activity_interactor.py` - only coordinate between services
- [x] 7. Update `actor_extractor.py` - thin wrapper calling actor_service
- [x] 8. Update `resource_extractor.py` - thin wrapper calling resource_service
- [x] 9. Update `payload_validator.py` - thin wrapper calling validation_service
- [x] 10. Update `response_builder.py` - thin wrapper calling response_service

### Step 3: Testing
- [x] 11. Verify the application still works correctly

## Note: Keep existing audit_service.py untouched (has existing logic)
