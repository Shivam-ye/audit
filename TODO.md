# Implementation Plan: Use tools_box CeleryBaseConfig

## Steps to complete:

- [x] 1. Update `audit/enums.py` - Add MessageStatus enum from tools_box
- [x] 2. Create `audit/errors.py` - Add CeleryErrors from tools_box
- [x] 3. Update `audit/models/message.py` - Add idempotency_key field to Message model
- [x] 4. Update `audit/tasks.py` - Use tools_box CeleryBaseConfig with custom subclass

## Implementation Details:

### Step 1: Update audit/enums.py ✅
Added MessageStatus import from tools_box.workers.enums

### Step 2: Create audit/errors.py ✅
Added CeleryErrors import from tools_box.workers.errors

### Step 3: Update audit/models/message.py ✅
Added required fields:
- idempotency_key (CharField, unique=True)
- attempt_counts (IntegerField)
- error (JSONField)

### Step 4: Update audit/tasks.py ✅
- Created AuditCeleryBaseConfig class that extends tools_box.workers.config.CeleryBaseConfig
- Overrode __init__ to use audit.models.Message instead of apps.payout.models.message.Message
- Added necessary imports from tools_box (NewRelicMetricsClientImpl, etc.)

