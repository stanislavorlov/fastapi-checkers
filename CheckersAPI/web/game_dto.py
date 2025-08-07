import datetime

from web.history_dto import HistoryDto


class GameDto:

    def __init__(self, game_id: str, name: str, started: datetime, history: list[HistoryDto]):
        self.game_id = game_id
        self.name = name
        self.started = started
        self.history = history
