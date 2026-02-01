from dataclasses import dataclass
from datetime import datetime, timezone, timedelta
from domain.kernel.entity import Entity
from domain.sessions.region import Region
from infrastructure.documents import PyObjectId


@dataclass
class PlayerSession(Entity):
    player_id: PyObjectId
    created_at: datetime
    expires_at: datetime
    token: str
    host: str
    agent: str
    region: Region
    tz_offset: timedelta      # in minutes, e.g. +120 for UTC+2

    @classmethod
    def create(cls, player_id: PyObjectId, session_token: str, host: str, agent: str, region: Region, tz: timezone = timezone.utc) -> 'PlayerSession':
        now = datetime.now(timezone.utc)
        return cls(
            player_id=player_id,
            created_at=now,
            expires_at=now + timedelta(days=7), # Extended session expiry
            token=session_token,
            host=host,
            agent=agent,
            region=region,
            tz_offset=tz.utcoffset(now) or timedelta(0)
        )