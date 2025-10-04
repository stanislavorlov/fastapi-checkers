import datetime
from typing import Optional
from pydantic import BaseModel

class Player(BaseModel):
    player_id: str
    username: Optional[str]

class Game(BaseModel):
    name: str
    started: datetime.datetime
    mode: str
    dark_player: str
    light_player: str

class History(BaseModel):
    game_id: str
    move: str
    captures: list[str]
    sequence: int
    player_id: str