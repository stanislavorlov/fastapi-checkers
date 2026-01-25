from typing import Optional, Any
from pydantic import ConfigDict
from infrastructure.documents import PyObjectId
from domain.kernel.value_object import ValueObject


class GameResult(ValueObject):
    winner_id: Optional[PyObjectId] = None
    reason: Optional[str] = None

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def __init__(self, winner_id: Optional[PyObjectId] = None, reason: Optional[str] = None, /, **data: Any):
        super().__init__(winner_id=winner_id, reason=reason, **data)

    def to_dict(self):
        return {"winner_id": str(self.winner_id), "reason": self.reason}