from domain.pdn_move import PdnMove


class HistoryEntry:

    def __init__(self, player_id: str, move: PdnMove, sequence: int, captures: list[str] = None):
        super().__init__()
        self.player_id = player_id
        self.move = move
        self.sequence = sequence
        self.captures = captures