import datetime
from games import History

class HistoryDto:
    def __init__(self, history: History):
        self.player_id = history['player_id']
        self.event_type = history['event_type']
        self.from_ = history['from_']
        self.to_ = history['to_']

class GameDto:

    def __init__(self, game_id: str, name: str, started: datetime, history: list[HistoryDto]):
        self.game_id = game_id
        self.name = name
        self.started = started
        self.history = history