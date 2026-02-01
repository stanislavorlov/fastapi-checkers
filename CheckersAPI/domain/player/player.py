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
from domain.player.player_identity import PlayerIdentity


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
    def create(cls, identity: PlayerIdentity, player_level: str = "1", profile: Optional[Profile] = None) -> "Player":
        """
        Unified factory method for all player types.
        """
        creation_map = {
            PlayerType.AI: cls._create_ai,
            PlayerType.GUEST: cls._create_human,
            PlayerType.ACCOUNT: cls._create_human,
        }

        creator = creation_map.get(identity.type_)
        if not creator:
            raise ValueError(f"No creation logic defined for player type: {identity.type_}")

        return creator(identity, player_level, profile)

    @classmethod
    def _create_ai(cls, identity: PlayerIdentity, *args, **kwargs) -> "Player":
        return cls(
            display_name=DisplayName(display_name="AI Bot"),
            _type=PlayerType.AI,
            _rank=Rank.intermediate(),
            _stats=PlayerStats.create_empty(),
            created_at=datetime.now(timezone.utc)
        )

    @classmethod
    def _create_human(cls, identity: PlayerIdentity, player_level: str, profile: Optional[Profile]) -> "Player":
        return cls(
            _type=identity.type_,
            display_name=DisplayName.from_contact(profile.contact) if profile else DisplayName.from_contact(Contact()),
            profile_id=identity.profile_id,
            _rank=Rank.from_level(player_level),
            _stats=PlayerStats.create_empty(),
            created_at=datetime.now(timezone.utc)
        )

    def create_session(self, session_token: str, host: str, agent: str, region: Optional[Region] = None, tz: timezone = timezone.utc) -> 'PlayerSession':
        # Default region if none provided
        session_region = region or Region(code="EU") # Use a valid default code
        session = PlayerSession.create(self.id, session_token, host, agent, session_region, tz)
        self.sessions.append(session)
        return session