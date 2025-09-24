import datetime
from pydantic import BaseModel

class Game(BaseModel):
    name: str
    started: datetime.datetime
    mode: str
    single_side: str

class History(BaseModel):
    game_id: str
    player_id: str
    event_type: str
    from_: str
    to_: str