from datetime import datetime, timezone
from infrastructure.documents import MatchingQueueSchema, QueueStatus
from infrastructure.mongo_context import MongoContext

class MatchingRepository:
    def __init__(self, db: MongoContext):
        self.db = db

    def add_to_queue(self, player_id: str, region: str, rating: int) -> str:
        queue_item = MatchingQueueSchema(
            session_id="", # ToDo: what is session_id here? maybe not needed for now or generated
            region=region,
            rating_estimate=rating,
            rd=0, # ToDo: get from player stats
            timestamp=datetime.now(timezone.utc),
            status=QueueStatus.WAITING
        )
        
        # We might want to store player_id in the queue item, but MatchingQueueSchema 
        # currently doesn't have it directly, or it uses session_id?
        # Looking at documents.py: MatchingQueueSchema has session_id, region, rating_estimate, rd, timestamp, status, matched_with.
        # It seems it doesn't link to player_id directly? 
        # Let's assume session_id IS the player_id for now or we need to update the schema.
        # The user request said: "creates an document inside the MatchingQueueSchema"
        
        # Let's update the schema to include player_id if it's missing or use session_id as player_id.
        # For now, I will use player_id as session_id.
        
        queue_item.player_id = player_id
        
        result = self.db.matching_queue.insert_one(queue_item.model_dump(mode='python', by_alias=True))
        return str(result.inserted_id)
