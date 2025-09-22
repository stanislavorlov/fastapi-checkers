import dataclasses
from domain.color import Color


class DomainEvent:
    def __init__(self, game_id: str):
        self.game_id = game_id

@dataclasses.dataclass(frozen=True)
class PieceCapturedEvent(DomainEvent):
    captured_at: int

@dataclasses.dataclass(frozen=True)
class PieceMovedEvent(DomainEvent):
    moved_from: int
    moved_to: int

@dataclasses.dataclass(frozen=True)
class TurnSwitchedEvent(DomainEvent):
    current_turn: Color