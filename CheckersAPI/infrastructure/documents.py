from datetime import datetime, timezone
from typing import Optional
from bson import ObjectId
from pydantic import BaseModel, Field


class UserSchema(BaseModel):
    user_id: str
    player_id: str
    email: str
    password_hash: str
    first_name: Optional[str]
    last_name: Optional[str]
    country: Optional[str]
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class UserSessionSchema(BaseModel):
    is_anonymous: bool
    token: str
    user_id: str
    host: str
    agent: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class PlayerRankSchema(BaseModel):
    rating: int             # ~1000–3000
    deviation: int          # 30–350, how uncertain we are about a player’s rating, more games -> bigger, less - slower
    last_update: datetime

class PlayerStatsSchema(BaseModel):
    games_played: int
    wins: int
    losses: int
    draws: int
    win_rate: float
    streak: int

class PlayerSchema(BaseModel):
    nickname: Optional[str] = None
    region: str
    rank_id: str
    stats_id: str
    is_anonymous: bool
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    model_config = {
        "arbitrary_types_allowed": True,
        "json_encoders": {ObjectId: str}
    }

class MatchingQueueSchema(BaseModel):
    player_id: str
    region: str
    rating_estimate: int
    rd: int
    timestamp: datetime
    status: str             # waiting | matched | timeout
    matched_with: Optional[str]  # optional when found

class GamePlayerSchema(BaseModel):
    player_id: str
    side: str

class GameResultSchema(BaseModel):
    winner_id: Optional[str] = None
    reason: str     # resignation | capture | draw

class GameSchema(BaseModel):
    name: str
    region: str
    created_at: datetime
    started_at: Optional[datetime]
    finished_at: Optional[datetime]
    result: GameResultSchema
    mode: str
    players: list[GamePlayerSchema]

class HistorySchema(BaseModel):
    game_id: str
    move: str
    captures: list[str]
    sequence: int
    player_id: str