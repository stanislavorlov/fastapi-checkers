from datetime import datetime
from pydantic import BaseModel
from web.history_dto import HistoryDto


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
