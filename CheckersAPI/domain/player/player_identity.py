from typing import Optional
from domain.kernel.value_object import ValueObject
from domain.player.player_type import PlayerType
from infrastructure.documents import PyObjectId

class PlayerIdentity(ValueObject):
    type_: PlayerType
    profile_id: Optional[PyObjectId] = None
    
    @classmethod
    def guest(cls):
        return cls(type_=PlayerType.GUEST)

    @classmethod
    def ai(cls):
        return cls(type_=PlayerType.AI)
        
    @classmethod
    def registered(cls, profile_id: PyObjectId):
        return cls(type_=PlayerType.ACCOUNT, profile_id=profile_id)
