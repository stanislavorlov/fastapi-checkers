from datetime import datetime, timezone
from typing import List

from infrastructure.documents import MatchingQueueSchema, QueueStatus, PyObjectId
from infrastructure.mongo_context import MongoContext

class MatchingRepository:
    def __init__(self, db: MongoContext):
        self.db = db

    def add_to_queue(self, player_id: str, region: str, rating: int) -> str:
        # Check if already in queue
        existing = self.db.matching_queue.find_one({"player_id": PyObjectId(player_id), "status": QueueStatus.WAITING})
        if existing:
            return str(existing["_id"])

        queue_item = MatchingQueueSchema(
            player_id=PyObjectId(player_id),
            region=region,
            rating_estimate=rating,
            rd=0, # ToDo: get from player stats
            timestamp=datetime.now(timezone.utc),
            status=QueueStatus.WAITING
        )
        
        result = self.db.matching_queue.insert_one(queue_item.model_dump(mode='python', by_alias=True))
        return str(result.inserted_id)

    def get_waiting_players(self) -> List[MatchingQueueSchema]:
        cursor = self.db.matching_queue.find({"status": QueueStatus.WAITING})
        return [MatchingQueueSchema(**doc) for doc in cursor]

    def mark_as_matched(self, player_id: str, opponent_id: str):
        self.db.matching_queue.update_one(
            {"player_id": PyObjectId(player_id), "status": QueueStatus.WAITING},
            {"$set": {"status": QueueStatus.MATCHED, "matched_with": PyObjectId(opponent_id)}}
        )
        self.db.matching_queue.update_one(
            {"player_id": PyObjectId(opponent_id), "status": QueueStatus.WAITING},
            {"$set": {"status": QueueStatus.MATCHED, "matched_with": PyObjectId(player_id)}}
        )
