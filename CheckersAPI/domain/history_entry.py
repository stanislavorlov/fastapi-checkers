from domain.events import EventType


class HistoryEntry:

    def __init__(self, player_id: str, type_: EventType, from_: str, to: str, sequence: int):
        super().__init__()
        self.player_id = player_id
        self.type_ = type_
        self.from_ = from_
        self.to = to
        self.sequence = sequence