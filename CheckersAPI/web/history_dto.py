from infrastructure.documents import History


class HistoryDto:
    def __init__(self, history: History):
        self.player_id : str = history['player_id']
        self.event_type : str = history['event_type']
        self.from_ : str = history['from_']
        self.to_ : str = history['to_']
