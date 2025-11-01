from typing import Optional
from bson import ObjectId
from domain.profile.profile import Profile
from infrastructure.mongo_context import MongoContext
from infrastructure.documents import ProfileSchema


class ProfileRepository:

    def __init__(self, db: MongoContext):
        self.db = db

    async def create(self, profile: Profile):
        result = await self.db.profiles.insert_one(ProfileSchema.model_dump(profile, by_alias=True))

        return str(result.inserted_id)
        # profile_document = ProfileSchema.model_validate(profile)
        #
        # return profile_collection.insert_one(profile_document)

    async def get(self, profile_id: str) -> Optional[Profile]:
        profile_document = await self.db.profiles.find_one({"_id": ObjectId(profile_id)})

        if not profile_document is None:
            return Profile(**profile_document)

        return None