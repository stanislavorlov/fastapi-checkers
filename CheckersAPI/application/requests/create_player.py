from dataclasses import dataclass
from typing import Optional
from domain.player.player_type import PlayerType
from infrastructure.documents import PyObjectId


@dataclass
class CreatePlayerRequest:
    type: PlayerType
    player_level: str
    profile_id: Optional[PyObjectId] = None