import uuid
from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass
class UserSession:
    id: str
    is_anonymous: bool
    created_at: datetime
    expires_at: datetime
    token: str
    host: str
    agent: str

    @property
    def is_active(self) -> bool:
        return self.expires_at < datetime.now(timezone.utc)

    @staticmethod
    def create(session_token: str, anonymous: bool, host: str, agent: str) -> 'UserSession':
        return UserSession(
            id=str(uuid.uuid4()),
            token=session_token,
            host=host,
            agent=agent,
            is_anonymous=anonymous,
            created_at=datetime.now(),
        )