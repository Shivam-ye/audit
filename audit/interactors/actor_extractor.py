from ..services.actor_service import ActorService


class ActorExtractor:
    """Thin wrapper - delegates to ActorService"""

    @staticmethod
    def extract(payload, validated, payload_type):
        """Delegate to ActorService"""
        return ActorService.extract_actor(payload, validated, payload_type)

