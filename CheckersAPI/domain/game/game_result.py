from typing import Optional, Any
from pydantic import ConfigDict
from infrastructure.documents import PyObjectId
from domain.kernel.value_object import ValueObject


class GameResult(ValueObject):
    winner: Optional[PyObjectId] = None
    reason: Optional[str] = None

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def to_dict(self):
        return {"winner": str(self.winner) if self.winner else None, "reason": self.reason}