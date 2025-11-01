import time
from datetime import datetime
from typing import Optional
from pydantic import Field
from domain.game.game_mode import GameMode
from domain.history_entry import HistoryEntry
from domain.kernel.aggregate_root import AggregateRoot
from domain.player.player import Player
from domain.side import Side


class Game(AggregateRoot):
    created_at: datetime = Field(..., alias="created_at")
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    result: dict        # GameResult.to_dict
    mode: GameMode
    history: list[HistoryEntry] = Field(..., alias="history")
    players: dict[Side, Player]  # {"dark": Player(...), "light": Player(...) }

    def assign_player(self, side: Side, player: Player):
        if not side in self.players:
            self.players[side] = player
        else:
            raise ValueError(f"Side {side} is already assigned")

    def start(self):
        if self.started_at is None:
            self.started_at = time.time()

    def append_history(self, history: HistoryEntry):
        self.history.append(history)