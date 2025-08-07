from infrastructure.database import history_collection
from infrastructure.documents import History
from domain.events import GameEvent
from web.history_dto import HistoryDto


class EventHandler:
    def __init__(self, game_id: str):
        self.game_id = game_id

    def handle(self, event: GameEvent):
        history = history_collection.find({'game_id': self.game_id})

        history_dtos = []
        for history in history:
            history_dtos.append(HistoryDto(history))

        #game_state = GameState(history_dtos)
        #game_state.apply(event)

        history = History(
            game_id=self.game_id,
            player_id=event.player_id,
            event_type=event.type,
            from_=event.from_,
            to_=event.to_
        )
        history_collection.insert_one(dict(history))
