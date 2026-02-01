from dataclasses import dataclass

@dataclass
class StartComputerGameRequest:
    player_id: str
    single_side: str
