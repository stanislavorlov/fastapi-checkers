import json
from domain.pdn_move import PdnMove


class EventParser:

    @staticmethod
    def parse(message_text: str):
        json_string = json.loads(message_text)

        player = str(json_string['playerId'])
        pdn_string = json_string['move']
        captured_squares = json_string['captured']

        return player, PdnMove(pdn_string, captured_squares)