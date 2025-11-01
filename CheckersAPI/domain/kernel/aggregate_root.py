from bson import ObjectId
from pydantic import BaseModel, Field
from infrastructure.documents import PyObjectId


class AggregateRoot(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")

    model_config = {
        "populate_by_name": True,  # allow both id= and _id=
        "arbitrary_types_allowed": True,  # for PyObjectId, datetime.timezone, etc.
        "json_encoders": {ObjectId: str},  # for Mongo serialization
    }

    def to_dict(self):
        """For repository persistence."""
        data = self.model_dump(by_alias=True)
        return data