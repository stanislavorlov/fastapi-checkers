import dataclasses
from domain.color import Color


class DomainEvent:
    def __init__(self, game_id: str):
        self.game_id = game_id

@dataclasses.dataclass(frozen=True)
class PieceCapturedEvent(DomainEvent):
    captured_at: int
    event_type: str = dataclasses.field(default='captured')

@dataclasses.dataclass(frozen=True)
class PieceMovedEvent(DomainEvent):
    moved_from: int
    moved_to: int
    event_type: str = dataclasses.field(default='moved')

@dataclasses.dataclass(frozen=True)
class TurnSwitchedEvent(DomainEvent):
    current_turn: Color
    event_type: str = dataclasses.field(default='turn')