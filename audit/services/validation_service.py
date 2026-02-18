from pydantic import ValidationError
from ..schemas import FlatActivity, ActivityWithObject, ActivityWithResource, AuditLogsPayload


class ValidationService:
    """Service for validating payloads - business logic moved from PayloadValidator"""

    @staticmethod
    def validate(payload):
        """
        Return validated object and its type ('object', 'resource', 'flat', or 'audit_logs')
        Handles both the new wrapped format and legacy formats.
        """
        print("FULL PAYLOAD:", payload)
        if not isinstance(payload, dict):
            raise ValueError(f"Invalid payload, expected dict but got {type(payload).__name__}: {payload}")

        # Check for new wrapped format with type: "audit_logs"
        if payload.get("type") == "audit_logs" and "payload" in payload:
            validated = AuditLogsPayload.model_validate(payload)
            # Return the inner payload for further processing
            inner_payload = validated.payload
            # Validate the inner payload as well
            return ValidationService._validate_inner_payload(inner_payload), "audit_logs"
        
        # Legacy format handling
        if "object" in payload and isinstance(payload["object"], dict) and "type" in payload["object"]:
            return ActivityWithObject.model_validate(payload), "object"
        elif "resource" in payload and isinstance(payload["resource"], dict) and "type" in payload["resource"]:
            return ActivityWithResource.model_validate(payload), "resource"
        else:
            return FlatActivity.model_validate(payload), "flat"

    @staticmethod
    def _validate_inner_payload(inner_payload):
        """
        Validate the inner payload from an audit_logs wrapper.
        """
        if not isinstance(inner_payload, dict):
            raise ValueError(f"Invalid inner payload, expected dict but got {type(inner_payload).__name__}: {inner_payload}")
        
        # Check for object or resource format
        if "object" in inner_payload and isinstance(inner_payload["object"], dict) and "type" in inner_payload["object"]:
            return ActivityWithObject.model_validate(inner_payload), "object"
        elif "resource" in inner_payload and isinstance(inner_payload["resource"], dict) and "type" in inner_payload["resource"]:
            return ActivityWithResource.model_validate(inner_payload), "resource"
        else:
            return FlatActivity.model_validate(inner_payload), "flat"

