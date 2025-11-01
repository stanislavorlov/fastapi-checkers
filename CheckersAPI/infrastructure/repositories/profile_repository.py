from typing import Optional
from bson import ObjectId
from domain.profile.full_name import FirstName, LastName
from domain.profile.profile import Profile
from infrastructure.mongo_context import MongoContext
from infrastructure.documents import ProfileSchema


class ProfileRepository:

    def __init__(self, db: MongoContext):
        self.db = db

    def create(self, profile: Profile):
        document = {
            **ProfileSchema.model_dump(profile, by_alias=True),
            "first_name" : profile.first_name.value,
            "last_name" : profile.last_name.value,
        }

        result = self.db.profiles.insert_one(document)

        return str(result.inserted_id)

    def get(self, profile_id: str) -> Optional[Profile]:
        profile_document = self.db.profiles.find_one({"_id": ObjectId(profile_id)})

        if not profile_document is None:
            return Profile(**profile_document)

        return None

    def find_by_email(self, email: str) -> Optional[Profile]:
        profile_document = self.db.profiles.find_one({"email": email})

        if profile_document is not None:
            return Profile(
                email=profile_document["email"],
                first_name=FirstName(profile_document["first_name"]),
                last_name=LastName(profile_document["last_name"]),
                password_hash=profile_document["password_hash"],
                username=profile_document["username"],
            )

        return None