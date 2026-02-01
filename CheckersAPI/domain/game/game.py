import time
from datetime import datetime
from typing import Optional
from bson import ObjectId
from pydantic import Field
from domain.game.game_mode import GameMode
from domain.history_entry import HistoryEntry
from domain.kernel.aggregate_root import AggregateRoot
from domain.player.player import Player
from domain.side import Side
from domain.game.game_result import GameResult
from domain.player.player_identity import PlayerIdentity


class Game(AggregateRoot):
    created_at: datetime = Field(..., alias="created_at")
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    result: dict        # GameResult.to_dict
    mode: GameMode
    history: list[HistoryEntry] = Field(..., alias="history")
    players: dict[Side, Player]  # {"dark": Player(...), "light": Player(...) }

    @classmethod
    def create_pve(cls, player: Player, player_side: Side) -> "Game":
        ai_bot = Player.create(PlayerIdentity.ai())
        ai_side = Side.Dark if player_side == Side.Light else Side.Light

        game = cls(
            created_at=datetime.now(),
            mode=GameMode.PVE,
            players={
                player_side: player,
                ai_side: ai_bot
            },
            history=[],
            result={}
        )
        game.start()
        return game

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

    def finish_game(self, winner_id: Optional[str], reason: str):
        self.finished_at = datetime.now()
        self.result = GameResult(winner=ObjectId(winner_id) if winner_id else None, reason=reason).to_dict()