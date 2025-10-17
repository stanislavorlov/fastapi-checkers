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
    anonymous: bool

class RequestComputerGameDto(BaseModel):
    player: GamePlayerDto
    side: str

class RequestOnlineGameDto(BaseModel):
    player: GamePlayerDto

class CreateUserDto(BaseModel):
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
    type: str
    exp: datetime
    iss: str
    aud: str

class AccessToken(BaseModel):
    access_token: str
    token_type: str = 'bearer'

class PlayerUserDto(BaseModel):
    player_id: str
    email: str
    first_name: str
    last_name: str
    country: str
    anonymous: bool