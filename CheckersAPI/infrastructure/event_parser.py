import json
from domain.events import GameEvent

class EventParser:
    def __init__(self):
        pass

    @staticmethod
    def parse(message_text: str) -> GameEvent:
        json_string = json.loads(message_text)

        if json_string['_type'] == 'move':
            print('move event')

        game_event = GameEvent(
            json_string['_playerId'],
            json_string['_type'],
            json_string['_from'],
            json_string['_to'])

        return game_event