from ..services.response_service import ResponseService


class ResponseBuilder:
    """Thin wrapper - delegates to ResponseService"""

    @staticmethod
    def build(actor_full, res_id, res_type, changes, summary):
        """Delegate to ResponseService"""
        return ResponseService.build_response(actor_full, res_id, res_type, changes, summary)

