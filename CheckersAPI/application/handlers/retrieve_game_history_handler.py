import logging
from application.handlers.base_handler import RequestHandler, TResponse
from application.requests.retrieve_game_history import RetrieveGameHistoryRequest
from infrastructure.repositories.history_repository import HistoryRepository

logger = logging.getLogger(__name__)

class RetrieveGameHistoryHandler(RequestHandler):

    def __init__(self, history_repo: HistoryRepository):
        self.history_repo = history_repo

    async def handle(self, request: RetrieveGameHistoryRequest) -> dict:
        logger.info(f"Retrieving game details for game {request.game_id}")
        return await self.history_repo.get_by_id(request.game_id)