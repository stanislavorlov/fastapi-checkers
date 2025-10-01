import json
from domain.events import GameEvent, EventType, GameEvents


class EventParser:

    @staticmethod
    def parse(message_text: str) -> GameEvents:
        json_string = json.loads(message_text)

        previous = json_string['_previous']
        current = json_string['_current']

        return GameEvents(EventParser.parse_event(previous), EventParser.parse_event(current))

    @staticmethod
    def parse_event(message_text: str) -> GameEvent:
        if not message_text or not len(message_text):
            return None

        try:
            json_string = json.loads(message_text)

            game_event = GameEvent(
                json_string['_playerId'],
                EventType.parse(json_string['_type']),
                json_string['_square'])

            return game_event

        except:
            return None