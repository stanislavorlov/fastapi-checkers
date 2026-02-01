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
    finished_at: datetime | None = None
    result: dict | None = None

class GamePlayerDto(BaseModel):
    player_id: str
    anonymous: bool

class RequestComputerGameDto(BaseModel):
    player: GamePlayerDto
    side: str

class StartComputerGameDto(BaseModel):
    singleSide: str

class RequestOnlineGameDto(BaseModel):
    player: GamePlayerDto

class CreateAccountDto(BaseModel):
    email: str
    password: str
    level: str
    first_name: str | None = None
    last_name: str | None = None
    country: str | None = None
    language: str | None = None

class AccessTokenData(BaseModel):
    sub: str
    preferred_username: str
    name: str
    type: str
    exp: datetime
    iss: str
    aud: str

class AccessToken(BaseModel):
    player_id: str
    access_token: str
    refresh_token: str
    name: str = ""
    email: str = ""
    type: str = ""
    token_type: str = 'bearer'

class RefreshTokenDto(BaseModel):
    refresh_token: str

class PlayerUserDto(BaseModel):
    player_id: str
    email: str
    first_name: str
    last_name: str
    country: str
    anonymous: bool

class RequestGameResponse(BaseModel):
    player_id: str
    status: str

class ProfileDto(BaseModel):
    email: str
    username: str
    first_name: str | None = None
    last_name: str | None = None
    language: str | None = None
    bio: str | None = None
    avatar_url: str | None = None
    country: str | None = None