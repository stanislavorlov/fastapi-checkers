from datetime import datetime, timezone, timedelta
from infrastructure.documents import SessionSchema, PyObjectId
from infrastructure.mongo_context import MongoContext
from bson import ObjectId


class SessionRepository:

    def __init__(self, db: MongoContext):
        self.db = db

    def create_session(self, player_id: PyObjectId, token: str, host: str, agent: str, region: str, timezone_name: str) -> str:
        document = SessionSchema(
            player_id=player_id,
            token=token,
            host=host,
            agent=agent,
            region=region,
            timezone=timezone_name,
        )

        result = self.db.sessions.insert_one(document.model_dump(mode='python', by_alias=True))

        return str(result.inserted_id)

    def find_recent_guest_session(self, host: str, agent: str, limit_hours: int = 24) -> str | None:
        """
        Finds a session for a given host and agent within the last limit_hours.
        Returns the player_id if found, else None.
        """
        threshold = datetime.now(timezone.utc) - timedelta(hours=limit_hours)

        query = {
            "host": host,
            "agent": agent,
            "created_at": {"$gte": threshold}
        }

        session = self.db.sessions.find_one(query, sort=[("created_at", -1)])

        if session:
            player_id = session["player_id"]
            if self.db.players.find_one({"_id": player_id}):
                return str(player_id)

        return None

    def find_session_by_player_and_client(self, player_id: str, host: str, agent: str) -> str | None:
        """
        Finds an existing session token for a specific player and client device.
        """
        query = {
            "player_id": ObjectId(player_id),
            "host": host,
            "agent": agent
        }
        session = self.db.sessions.find_one(query, sort=[("created_at", -1)])
        return session["token"] if session else None