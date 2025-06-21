import datetime
from pydantic import BaseModel

class Game(BaseModel):
    name: str
    started: datetime.datetime
