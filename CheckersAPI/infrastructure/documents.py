from datetime import datetime, timezone
from enum import Enum
from typing import Optional, Literal, List
from bson import ObjectId
from pydantic import BaseModel, Field, GetCoreSchemaHandler
from pydantic_core import core_schema


# ---------------------------
# Custom ObjectId validator
# ---------------------------
class PyObjectId(ObjectId):
    """Pydantic v2-compatible wrapper for MongoDB ObjectId."""

    @classmethod
    def __get_pydantic_core_schema__(cls, source_type, handler: GetCoreSchemaHandler):
        return core_schema.no_info_plain_validator_function(cls.validate)

    @classmethod
    def validate(cls, v):
        if isinstance(v, ObjectId):
            return v
        if not ObjectId.is_valid(v):
            raise ValueError(f"Invalid ObjectId: {v}")
        return ObjectId(v)

    @classmethod
    def __get_pydantic_json_schema__(cls, schema, handler):
        return {"type": "string", "pattern": "^[a-fA-F0-9]{24}$"}


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


class ProfileSchema(BaseModel):
    """
    Profile is created during user registration
    """
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
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

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class PlayerSchema(BaseModel):
    """
    Player is created during starting the game. Since anonymous can be created only at that stage.
    """
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    type: PlayerType
    display_name: str
    profile_id: Optional[PyObjectId] = None  # present for registered accounts

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class SessionSchema(BaseModel):
    """
    Session is going to be added while authenticating a user or starting a game
    """
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    player_id: PyObjectId  # always a PlayerSchema ID
    token: str
    host: str
    agent: str
    region: str
    timezone: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class RankSchema(BaseModel):
    """
    Rank schema to be created during the player creation
    """
    player_id: PyObjectId
    rating: int             # ~1000–3000
    deviation: int          # 30–350, how uncertain we are about a player’s rating, more games -> bigger, less - slower
    last_update: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class StatsSchema(BaseModel):
    """
    Rank schema to be created during the player creation
    """
    player_id: str
    games_played: int = 0
    wins: int = 0
    losses: int = 0
    draws: int = 0
    win_rate: float = 0.0
    streak: int = 0

class MatchingQueueSchema(BaseModel):
    """
    Player requests a game, enters matching.
    """
    session_id: str
    region: str
    rating_estimate: int
    rd: int
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    status: QueueStatus = QueueStatus.WAITING
    matched_with: Optional[PyObjectId] = None

class GamePlayerSchema(BaseModel):
    player_id: PyObjectId
    color: PlayerColor
    snapshot: Optional[dict] = None  # store display_name/type at game creation

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class GameSchema(BaseModel):
    """
    When a match is found
    """
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    result: Optional[dict] = None  # { winner: ObjectId | null, reason: str | null }
    mode: GameMode
    players: List[GamePlayerSchema]

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class HistorySchema(BaseModel):
    game_id: PyObjectId
    move: str
    captures: List[str] = []
    sequence: int

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

# Account → for authenticated users
# Player → for all participants (guest or account)
# Game → the actual checkers match
# accounts

# For authenticated users (login credentials, email, password, etc.)
# {
#   _id: ObjectId,
#   email: String,
#   password_hash: String,
#   created_at: Date
# }
# players
# For any user identity (authenticated or guest)
# {
#   _id: ObjectId,                 // always required
#   type: "guest" | "account",
#   display_name: String,
#   account_id: ObjectId,          // only for type === "account"
#   created_at: Date,
#   last_seen: Date
# }
# games
# {
#   _id: ObjectId,
#   players: [
#     { player_id: ObjectId, color: "white" },
#     { player_id: ObjectId, color: "black" }
#   ],
#   moves: [String],
#   started_at: Date,
#   ended_at: Date,
#   result: {
#     winner: ObjectId,
#     reason: String
#   }
# }

# from pydantic import BaseModel, Field
# from typing import Literal, List, Optional
# from bson import ObjectId
# from datetime import datetime
#
# class PyObjectId(ObjectId):
#     @classmethod
#     def __get_validators__(cls):
#         yield cls.validate
#     @classmethod
#     def validate(cls, v):
#         if not ObjectId.is_valid(v):
#             raise ValueError("Invalid ObjectId")
#         return ObjectId(v)
#
# class PlayerSnapshot(BaseModel):
#     display_name: str
#     type: Literal["guest", "account"]
#
# class GamePlayer(BaseModel):
#     player_id: PyObjectId
#     color: Literal["white", "black"]
#     snapshot: Optional[PlayerSnapshot] = None
#     rating_before: Optional[float] = None
#     rating_after: Optional[float] = None
#
# class GameSchema(BaseModel):
#     id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
#     mode: Literal["pvp", "pve"]
#     players: List[GamePlayer]
#     moves: List[str] = []
#     result: Optional[dict] = None
#     started_at: datetime = Field(default_factory=datetime.utcnow)
#     ended_at: Optional[datetime] = None
