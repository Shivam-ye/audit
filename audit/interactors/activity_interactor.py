import logging
from typing import List
from ..services.audit_service import compute_diff, generate_summary, verb_map
from ..services.validation_service import ValidationService
from ..services.actor_service import ActorService
from ..services.resource_service import ResourceService
from ..services.history_service import HistoryService
from ..services.response_service import ResponseService

logger = logging.getLogger(__name__)


class ActivityInteractor:
    """Interactor for orchestrating the activity processing flow - only interaction logic"""

    @staticmethod
    def process_payloads(payloads):
        """
        Process payloads - orchestration only, delegates to services.
        
        Args:
            payloads: Single payload dict or list of payload dicts
            
        Returns:
            List of response dictionaries
        """
        # If a single dict is passed, wrap it in a list
        if isinstance(payloads, dict):
            payloads = [payloads]

        result = []
        for payload in payloads:
            # Step 1: Validate payload - delegates to ValidationService
            validated, payload_type = ValidationService.validate(payload)
            logger.info(f"Validated payload_type: {payload_type}")
            
            # Step 2: Extract actor - delegates to ActorService
            actor_full, actor_id = ActorService.extract_actor(payload, validated, payload_type)
            logger.info(f"Extracted actor_full: {actor_full}, actor_id: {actor_id}")
            
            # Step 3: Extract resource - delegates to ResourceService
            res_id, res_type, data = ResourceService.extract_resource(payload, validated, payload_type)
            logger.info(f"Extracted res_id: {res_id}, res_type: {res_type}, data: {data}")
            
            # Step 4: Get verb mapping from audit_service
            verb_raw = payload.get("verb", "updated").lower().strip()
            verb = verb_map.get(verb_raw, "updated")
            logger.info(f"Verb mapped: {verb_raw} -> {verb}")

            # Step 5: Validate resource type required for create/update
            if res_type == "unknown" and verb not in ["deleted", "delete"]:
                raise ValueError("Resource type is required for create/update")

            # Step 6: Get last history - delegates to HistoryService
            last = HistoryService.get_last_history(res_type, res_id)
            logger.info(f"Last history: {last}")
            
            # Step 7: Compute diff using audit_service
            old = last.full_fields_after if last else {}
            logger.info(f"Old data (full_fields_after): {old}")
            logger.info(f"New data (data): {data}")
            changes = compute_diff(old, data)
            logger.info(f"Computed changes: {changes}")
            summary = generate_summary(changes)

            # Step 8: Create history record - delegates to HistoryService
            HistoryService.create_history(
                res_type=res_type,
                res_id=res_id,
                operation=verb,
                actor_full=actor_full,
                actor_id=actor_id,
                changes=changes,
                summary=summary,
                data=data,
                last_version=last.version if last else None
            )

            # Step 9: Build response - delegates to ResponseService
            response = ResponseService.build_response(actor_full, res_id, res_type, changes, summary)
            response["verb"] = verb
            result.append(response)

        return result
