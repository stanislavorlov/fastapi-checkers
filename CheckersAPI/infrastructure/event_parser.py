import json
from domain.events import GameEvent, EventType


class EventParser:
    def __init__(self):
        pass

    @staticmethod
    def parse(message_text: str) -> GameEvent:
        json_string = json.loads(message_text)

        print(json_string)

        game_event = GameEvent(
            json_string['_playerId'],
            EventType.parse(json_string['_type']),
            json_string['_from'],
            json_string['to'])

        return game_event