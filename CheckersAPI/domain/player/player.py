from datetime import timezone, datetime
from typing import Optional, List
from pydantic import Field
from domain.kernel.aggregate_root import AggregateRoot
from domain.player.display_name import DisplayName
from domain.player.player_type import PlayerType
from domain.player.rank import Rank
from domain.player.stats import PlayerStats
from domain.profile.contact import Contact
from domain.profile.profile import Profile
from domain.sessions.player_session import PlayerSession
from domain.sessions.region import Region
from infrastructure.documents import PyObjectId


class Player(AggregateRoot):
    type_: PlayerType = Field(PlayerType.GUEST, alias="_type")
    display_name: Optional[DisplayName] = Field(None, alias="display_name")
    profile_id: Optional[PyObjectId] = None
    sessions: List[PlayerSession] = []
    rank: Rank = Field(None, alias="_rank")
    stats: PlayerStats = Field(None, alias="_stats")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    def update_player(self, display_name: DisplayName, type_: PlayerType) -> None:
        self.display_name = display_name
        self.type_ = type_

    @classmethod
    def create(cls, type_: PlayerType, player_level: str, profile: Optional[Profile]) -> "Player":
        return cls(
            type_=type_,
            display_name=DisplayName.from_contact(profile.contact) if profile else DisplayName.from_contact(Contact()),
            profile_id=profile.id if profile else None,
            rank=Rank.from_level(player_level),
            stats=PlayerStats.create_empty(),
            created_at=datetime.now(timezone.utc))

    def create_session(self, session_token: str, host: str, agent: str, region: Region, tz: timezone) -> 'PlayerSession':
        self.sessions.append(PlayerSession.create(self.id, session_token, host, agent, region, tz))