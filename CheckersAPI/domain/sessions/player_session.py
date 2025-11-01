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

    @staticmethod
    def create(player_id: PyObjectId, session_token: str, host: str, agent: str, region: Region, tz: timezone) -> 'PlayerSession':
        return PlayerSession(
            player_id=player_id,
            created_at=datetime.now(),
            expires_at=datetime.now() + timedelta(minutes=20),
            token=session_token,
            host=host,
            agent=agent,
            region=region,
            tz_offset=tz.utc.utcoffset(datetime.now())
        )