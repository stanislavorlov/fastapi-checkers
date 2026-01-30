from pydantic import BaseModel


class HistoryEntry(BaseModel):
    player_id: str
    pdn_string: str
    sequence: int
    captures: list[str] = []