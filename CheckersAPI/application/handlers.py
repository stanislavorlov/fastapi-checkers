import json
from dataclasses import asdict

from domain.board import Board
from infrastructure.database import history_collection
from infrastructure.documents import History
from domain.events import GameEvent
from infrastructure.connnection_manager import ConnectionManager
from web.history_dto import HistoryDto


class EventHandler:
    def __init__(self, game_id: str, manager: ConnectionManager):
        self.game_id = game_id
        self.manager = manager

    async def handle(self, event: GameEvent):
        print('Event handler called -> handle')

        history = history_collection.find({'game_id': self.game_id})

        board = Board()

        history_dtos = []
        for item in history:
            history_dto = HistoryDto(item)
            history_dtos.append(history_dto)

            parsed_from = int(history_dto.from_)
            parsed_to = int(history_dto.to_)
            board.move_piece(parsed_from, parsed_to)

        print(f"from: {event.from_}, to: {event.to_}")

        board.move_piece(int(event.from_), int(event.to_))

        for board_event in board.events:
            await self.manager.broadcast(self.game_id, json.dumps(asdict(board_event)))

        history = History(
            game_id=self.game_id,
            player_id=event.player_id,
            event_type=event.type.value(),
            from_=event.from_,
            to_=event.to_
        )
        #history_collection.insert_one(dict(history))
