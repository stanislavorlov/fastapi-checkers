import datetime
from typing import Optional
from pydantic import BaseModel

class User(BaseModel):
    user_id: str
    email: str
    password_hash: str
    first_name: Optional[str]
    last_name: Optional[str]
    country: Optional[str]

class GlickoRank(BaseModel):
    rating: int
    rd: int
    vol: float

class PlayerRank(BaseModel):
    elo: int
    glicko: GlickoRank
    last_update: datetime.datetime

class PlayerStats(BaseModel):
    games_played: int
    wins: int
    losses: int
    draws: int
    win_rate: float
    streak: int

class Player(BaseModel):
    user_id: Optional[str]
    is_anonymous: bool
    region: str         # EU
    rank: PlayerRank
    stats: PlayerStats

class MatchingQueue(BaseModel):
    player_id: str
    region: str
    rating_estimate: int
    rd: int
    timestamp: datetime.datetime
    status: str             # waiting | matched | timeout
    matched_with: Optional[str]  # optional when found

class GamePlayer(BaseModel):
    player_id: str
    side: str
    #requestor: bool

class GameResult(BaseModel):
    winner_id: Optional[str] = None
    reason: str     # resignation | capture | draw

class Game(BaseModel):
    name: str
    region: str
    created_at: datetime.datetime
    started_at: Optional[datetime.datetime]
    finished_at: Optional[datetime.datetime]
    result: GameResult
    mode: str
    players: list[GamePlayer]

class History(BaseModel):
    game_id: str
    move: str
    captures: list[str]
    sequence: int
    player_id: str