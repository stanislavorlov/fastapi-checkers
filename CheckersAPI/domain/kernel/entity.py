from pydantic import BaseModel, Field
from infrastructure.documents import PyObjectId


class Entity(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")

    def to_dict(self):
        """For repository persistence."""
        data = self.model_dump(by_alias=True)
        return data