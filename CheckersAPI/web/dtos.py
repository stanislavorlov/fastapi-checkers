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

class WriteGameDto(BaseModel):
    name: str
    started: datetime
    mode: str
    light_player: str
    dark_player: str
