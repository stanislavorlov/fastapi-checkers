import logging
from application.handlers.base_handler import RequestHandler, TResponse
from application.requests.retrieve_player_history import RetrievePlayerHistoryRequest
from infrastructure.repositories.history_repository import HistoryRepository

logger = logging.getLogger(__name__)

class RetrievePlayerHistoryHandler(RequestHandler):

    def __init__(self, history_repo: HistoryRepository):
        self.history_repo = history_repo

    async def handle(self, request: RetrievePlayerHistoryRequest) -> list:
        logger.info(f"Retrieving player history for player {request.player_id}")
        return await self.history_repo.fetch_archived_games(request.player_id)