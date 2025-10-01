from pydantic import BaseModel


class HistoryDto(BaseModel):
    player_id: str
    event_type: str
    from_: int
    to: int
    sequence: int
