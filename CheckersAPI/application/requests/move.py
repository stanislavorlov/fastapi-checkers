from dataclasses import dataclass

@dataclass
class MoveRequest:
    game_id: str
    player_id: str
    data: any
