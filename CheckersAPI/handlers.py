from database import history_collection
from games import History


class GameEvent:
    def __init__(self, player_id: str, type_: str, from_: str, to_: str):
        self.player_id = player_id
        self.type = type_
        self.from_ = from_
        self.to_ = to_

class EventHandler:
    def __init__(self, game_id: str):
        self.game_id = game_id

    def handle(self, event: GameEvent):
        history = History(
            game_id=self.game_id,
            player_id=event.player_id,
            event_type=event.type,
            from_=event.from_,
            to_=event.to_
        )
        history_collection.insert_one(dict(history))
