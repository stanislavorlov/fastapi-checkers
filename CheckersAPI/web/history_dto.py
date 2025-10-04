from pydantic import BaseModel


class HistoryDto(BaseModel):
    player_id: str
    move: str
    captures: list[str]
    sequence: int
