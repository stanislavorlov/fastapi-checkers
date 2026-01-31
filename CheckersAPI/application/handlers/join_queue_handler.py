import logging
from infrastructure.repositories.matching_repository import MatchingRepository

logger = logging.getLogger(__name__)

class JoinQueueHandler:
    def __init__(self, matching_repository: MatchingRepository):
        self.matching_repository = matching_repository

    async def handle(self, player_id: str):
        # Add to matching queue
        self.matching_repository.add_to_queue(player_id=player_id, region="EU", rating=1000)
