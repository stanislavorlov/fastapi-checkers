from typing import Optional
from pydantic import Field
from domain.kernel.entity import Entity
from domain.player.player_type import PlayerType
from infrastructure.documents import PyObjectId


class GamePlayer(Entity):
    player_id: PyObjectId
    display_name: Optional[str] = None
    player_type: PlayerType = Field(PlayerType.GUEST, alias="_type")