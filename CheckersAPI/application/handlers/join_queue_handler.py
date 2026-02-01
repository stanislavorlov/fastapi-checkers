import logging
from infrastructure.repositories.matching_repository import MatchingRepository
from application.handlers.base_handler import RequestHandler
from application.requests.join_queue import JoinQueueRequest

logger = logging.getLogger(__name__)

class JoinQueueHandler(RequestHandler[JoinQueueRequest, None]):
    def __init__(self, matching_repository: MatchingRepository):
        self.matching_repository = matching_repository

    async def handle(self, request: JoinQueueRequest):
        player_id = request.player_id
        # Add to matching queue
        self.matching_repository.add_to_queue(player_id=player_id, region="EU", rating=1000)
