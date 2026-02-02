from dataclasses import dataclass


@dataclass(frozen=True)
class RetrievePlayerHistoryRequest:
    player_id: str