import json
from dataclasses import asdict
from typing import List
from domain.board import Board
from domain.board_history import BoardHistory
from domain.history_entry import HistoryEntry
from domain.side import Side
from infrastructure.database import history_collection
from infrastructure.documents import History
from domain.events import GameEvent, EventType, GameEvents
from infrastructure.connnection_manager import ConnectionManager
from infrastructure.schemas import individual_history, list_histories


class EventHandler:
    def __init__(self, game_id: str, manager: ConnectionManager):
        self.game_id = game_id
        self.manager = manager

    async def handle(self, game_events: GameEvents):
        print('Event handler called -> handle')

        history = history_collection.find({'game_id': self.game_id}).sort('sequence', 1)
        board_history = BoardHistory(list_histories(history))
        board = Board().from_history(board_history)

        current, previous = game_events.cur, game_events.prev

        print(f"Player {current.player_id} making {current.type.value()} with previous {previous.type.value()} action")

        if current.type == EventType.move() or current.type == EventType.capture() or current.type == EventType.promote():
            board.move_piece(previous.square, current.square)

        for board_event in board.flush_events():
            # noinspection PyDataclass
            await self.manager.broadcast(self.game_id, json.dumps(asdict(board_event)))

        history = History(
            game_id=self.game_id,
            player_id=current.player_id,
            event_type=event.type.value(),
            square=event.square,
            sequence=len(history),
        )
        #history_collection.insert_one(dict(history))
