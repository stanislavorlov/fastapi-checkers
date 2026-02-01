from domain.pdn_move import PdnMove


class EventParser:

    @staticmethod
    def parse(data: dict):
        player = str(data['playerId'])
        pdn_string = data['move']
        captured_squares = data['captured']

        return player, PdnMove(pdn_string, captured_squares)