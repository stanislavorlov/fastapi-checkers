from datetime import datetime, timezone
from enum import Enum
from typing import Optional, List, Any
from bson import ObjectId
from pydantic import BaseModel, Field, ConfigDict
from pydantic_core import core_schema


# ---------------------------
# Custom ObjectId validator
# ---------------------------
class PyObjectId(ObjectId):
    @classmethod
    def __get_pydantic_core_schema__(cls, _source_type: Any, _handler: Any) -> core_schema.CoreSchema:
        return core_schema.json_or_python_schema(
            json_schema=core_schema.chain_schema([
                core_schema.str_schema(),
                core_schema.no_info_plain_validator_function(cls.validate),
            ]),
            python_schema=core_schema.union_schema([
                core_schema.is_instance_schema(ObjectId),
                core_schema.chain_schema([
                    core_schema.str_schema(),
                    core_schema.no_info_plain_validator_function(cls.validate),
                ]),
            ]),
            serialization=core_schema.plain_serializer_function_ser_schema(
                lambda x: str(x),
                when_used='json'
            ),
        )

    @classmethod
    def validate(cls, value: Any) -> ObjectId:
        if not ObjectId.is_valid(value):
            raise ValueError("Invalid ObjectId")
        return ObjectId(value)

# ---------------------------
# Enums
# ---------------------------
class PlayerType(str, Enum):
    GUEST = "guest"
    ACCOUNT = "account"

class GameMode(str, Enum):
    PVP = "pvp"
    PVE = "pve"

class PlayerColor(str, Enum):
    WHITE = "white"
    BLACK = "black"

class QueueStatus(str, Enum):
    WAITING = "waiting"
    MATCHED = "matched"
    TIMEOUT = "timeout"

# ---------------------------
# Models
# ---------------------------
class ProfileSchema(BaseModel):
    """
    Profile is created during user registration
    """
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    email: str
    password_hash: str
    username: str
    locked: bool = False
    join_date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    initial_level: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    language: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    country: Optional[str] = None

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
    )

class SessionSchema(BaseModel):
    """
    Session is stored in standalone sessions collection
    """
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    player_id: PyObjectId
    token: str
    host: str
    agent: str
    region: str
    timezone: str
    expires_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
    )

class PlayerSchema(BaseModel):
    """
    Player is created during starting the game. Since anonymous can be created only at that stage.
    """
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    type: PlayerType
    display_name: str
    profile_id: Optional[PyObjectId] = None  # present for registered accounts
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
    )

class RankSchema(BaseModel):
    """
    Rank schema to be created during the player creation
    """
    player_id: PyObjectId
    rating: int             # ~1000–3000
    deviation: int          # 30–350, how uncertain we are about a player’s rating, more games -> bigger, less - slower
    last_update: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
    )

class StatsSchema(BaseModel):
    """
    Stats schema to be created during the player creation
    """
    player_id: PyObjectId
    games_played: int = 0
    wins: int = 0
    losses: int = 0
    draws: int = 0
    win_rate: float = 0.0
    streak: int = 0

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
    )

class MatchingQueueSchema(BaseModel):
    """
    Player requests a game, enters matching.
    """
    player_id: PyObjectId
    region: str
    rating_estimate: int
    rd: int
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    status: QueueStatus = QueueStatus.WAITING
    matched_with: Optional[PyObjectId] = None

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
    )

class GamePlayerSchema(BaseModel):
    player_id: PyObjectId
    color: PlayerColor
    snapshot: Optional[dict] = None  # store display_name/type at game creation

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
    )

class GameResult(BaseModel):
    winner: Optional[PyObjectId] = None
    reason: Optional[str] = None

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
    )

class GameSchema(BaseModel):
    """
    When a match is found
    """
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    result: Optional[GameResult] = None
    mode: GameMode
    players: List[GamePlayerSchema]
    archived_history: Optional[str] = None

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
    )

class HistorySchema(BaseModel):
    game_id: PyObjectId
    player_id: PyObjectId
    pdn_string: str
    captures: List[str] = []
    sequence: int

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
    )
