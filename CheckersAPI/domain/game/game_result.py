from typing import Optional
from bson import ObjectId
from domain.kernel.value_object import ValueObject


class GameResult(ValueObject):
    def __init__(self, winner_id: Optional[ObjectId], reason: Optional[str]):
        self.winner_id = winner_id
        self.reason = reason

    def to_dict(self):
        return {"winner_id": str(self.winner_id), "reason": self.reason}