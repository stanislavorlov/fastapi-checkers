from dataclasses import dataclass


@dataclass(frozen=True)
class RetrieveGameHistoryRequest:
    game_id: str