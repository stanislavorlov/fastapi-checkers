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

        result = self.db.sessions.insert_one(document)

        return str(result.inserted_id)