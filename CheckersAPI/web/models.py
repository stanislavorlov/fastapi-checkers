from datetime import datetime
from pydantic import BaseModel

class HistoryDto(BaseModel):
    player_id: str
    move: str
    captures: list[str]
    sequence: int

class ReadGameDto(BaseModel):
    game_id: str
    name: str
    started: datetime
    mode: str
    light_player: str
    dark_player: str
    history: list[HistoryDto]

class GamePlayerDto(BaseModel):
    player_id: str
    side: str
    requestor: bool
    anonymous: bool

class WriteGameDto(BaseModel):
    name: str
    started: datetime
    mode: str
    players: list[GamePlayerDto]

class CreateUser(BaseModel):
    email: str
    password: str
    level: str
    first_name: str | None = None
    last_name: str | None = None
    country: str | None = None

class AccessTokenData(BaseModel):
    sub: str
    preferred_username: str
    name: str