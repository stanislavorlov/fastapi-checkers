from dataclasses import dataclass

@dataclass
class AbandonGameRequest:
    game_id: str
    player_id: str
