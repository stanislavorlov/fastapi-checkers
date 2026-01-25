from datetime import datetime, timezone
from infrastructure.documents import MatchingQueueSchema, QueueStatus, PyObjectId
from infrastructure.mongo_context import MongoContext

class MatchingRepository:
    def __init__(self, db: MongoContext):
        self.db = db

    def add_to_queue(self, player_id: str, region: str, rating: int) -> str:
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
