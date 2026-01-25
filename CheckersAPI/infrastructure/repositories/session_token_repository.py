from datetime import datetime, timezone, timedelta
from infrastructure.documents import SessionSchema, PyObjectId
from infrastructure.mongo_context import MongoContext


class SessionRepository:

    def __init__(self, db: MongoContext):
        self.db = db

    def create_session(self, player_id: PyObjectId, token: str, host: str, agent: str, region: str, timezone: str) -> str:
        document = SessionSchema(
            player_id=player_id,
            token=token,
            host=host,
            agent=agent,
            region=region,
            timezone=timezone,
        )

        result = self.db.sessions.insert_one(document.model_dump(mode='python', by_alias=True))

        return str(result.inserted_id)

    def find_recent_guest_session(self, host: str, agent: str, limit_hours: int = 24) -> str | None:
        """
        Finds a session for a given host and agent within the last limit_hours.
        Returns the player_id if found, else None.
        """
        # Ensure we are working with naive datetimes or consistent timezones
        threshold = datetime.now(timezone.utc) - timedelta(hours=limit_hours)

        # We look for the most recent session
        query = {
            "host": host,
            "agent": agent,
            "created_at": {"$gte": threshold}
        }

        # Find the most recent session matching criteria
        session = self.db.sessions.find_one(query, sort=[("created_at", -1)])

        if session:
            # We also need to check if the player still exists
            player_id = session["player_id"]
            if self.db.players.find_one({"_id": player_id}):
                return str(player_id)

        return None