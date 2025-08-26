class GameEvent:
    def __init__(self, player_id: str, type_: str, from_: str, to_: str):
        self.player_id = player_id
        self.type = type_
        self.from_ = from_
        self.to_ = to_