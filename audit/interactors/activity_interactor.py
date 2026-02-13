from typing import List, Dict
from ..services.audit_service import compute_diff, generate_summary, verb_map
from .payload_validator import PayloadValidator
from .actor_extractor import ActorExtractor
from .resource_extractor import ResourceExtractor
from .response_builder import ResponseBuilder
from ..models import AuditHistory
from django.utils import timezone

class ActivityInteractor:
    @staticmethod
    def process_payloads(payloads):
        # If a single dict is passed, wrap it in a list
        if isinstance(payloads, dict):
            payloads = [payloads]

        result = []
        for payload in payloads:
            validated, payload_type = PayloadValidator.validate(payload)
            actor_full, actor_id = ActorExtractor.extract(payload, validated, payload_type)
            res_id, res_type, data = ResourceExtractor.extract(payload, validated, payload_type)
            verb_raw = payload.get("verb", "updated").lower().strip()
            verb = verb_map.get(verb_raw, "updated")

            if res_type == "unknown" and verb not in ["deleted", "delete"]:
                raise ValueError("Resource type is required for create/update")

            last = AuditHistory.objects.filter(
                resource_type=res_type,
                resource_id=res_id
            ).order_by('-version').first()

            old = last.full_fields_after if last else {}
            changes = compute_diff(old, data)
            summary = generate_summary(changes)
            now = timezone.now()

            AuditHistory.objects.create(
                resource_type=res_type,
                resource_id=res_id,
                version=(last.version + 1) if last else 1,
                operation=verb,
                actor=actor_full,
                actor_id=actor_id,
                changes=changes,
                summary=summary,
                full_fields_after=data,
                timestamp=now,
            )

            response = ResponseBuilder.build(actor_full, res_id, res_type, changes, summary)
            response["verb"] = verb
            result.append(response)

        return result

    # @staticmethod
    # def process_payloads(payloads: List[Dict]) -> List[Dict]:
    #     result = []

    #     for payload in payloads:
    #         # Validate payload
    #         validated, payload_type = PayloadValidator.validate(payload)

    #         # Extract actor
    #         actor_full, actor_id = ActorExtractor.extract(payload, validated, payload_type)

    #         # Extract resource info & data
    #         res_id, res_type, data = ResourceExtractor.extract(payload, validated, payload_type)

    #         # Verb mapping
    #         verb_raw = payload.get("verb", "updated").lower().strip()
    #         verb = verb_map.get(verb_raw, "updated")

    #         # Check resource type
    #         if res_type == "unknown" and verb not in ["deleted", "delete"]:
    #             raise ValueError("Resource type is required for create/update")

    #         # Diff & save
    #         last = AuditHistory.objects.filter(
    #             resource_type=res_type,
    #             resource_id=res_id
    #         ).order_by('-version').first()

    #         old = last.full_fields_after if last else {}
    #         changes = compute_diff(old, data)
    #         summary = generate_summary(changes)
    #         now = timezone.now()

    #         AuditHistory.objects.create(
    #             resource_type=res_type,
    #             resource_id=res_id,
    #             version=(last.version + 1) if last else 1,
    #             operation=verb,
    #             actor=actor_full,
    #             actor_id=actor_id,
    #             changes=changes,
    #             summary=summary,
    #             full_fields_after=data,
    #             timestamp=now,
    #         )

    #         # Build response
    #         response = ResponseBuilder.build(actor_full, res_id, res_type, changes, summary)
    #         response["verb"] = verb
    #         result.append(response)

    #     return result

