import logging
from typing import Optional
from bson import ObjectId
from domain.profile.contact import Contact
from domain.profile.full_name import FullName
from domain.profile.profile import Profile
from infrastructure.mongo_context import MongoContext


logger = logging.getLogger(__name__)

class ProfileRepository:

    def __init__(self, db: MongoContext):
        self.db = db

    def create(self, profile: Profile):
        document = {
            "email": profile.contact.email,
            "password_hash": profile.password_hash,
            "username": profile.contact.username,
            "initial_level": profile.initial_level,
            "first_name": profile.full_name.first.value,
            "last_name": profile.full_name.last.value,
            "language": profile.language,
            "bio": profile.bio,
            "avatar_url": profile.avatar_url,
            "country": profile.country
        }

        result = self.db.profiles.insert_one(document)

        return str(result.inserted_id)

    def get(self, profile_id: str) -> Optional[Profile]:
        profile_document = self.db.profiles.find_one({"_id": ObjectId(profile_id)})

        if not profile_document is None:
            return Profile(
                _id=profile_document["_id"],
                contact=Contact(
                    contact=f"{profile_document["username"]} <{profile_document["email"]}>",
                ),
                password_hash=profile_document["password_hash"],
                full_name=FullName.create(profile_document["first_name"], profile_document["last_name"]),
                initial_level=profile_document["initial_level"],
                language=profile_document["language"],
                bio=profile_document["bio"],
                avatar_url=profile_document["avatar_url"],
                country=profile_document["country"]
            )
        return None

    def save(self, profile: Profile):
        document = {
            "email": profile.contact.email,
            "password_hash": profile.password_hash,
            "username": profile.contact.username,
            "initial_level": profile.initial_level,
            "first_name": profile.full_name.first.value if profile.full_name else None,
            "last_name": profile.full_name.last.value if profile.full_name else None,
            "language": profile.language,
            "bio": profile.bio,
            "avatar_url": profile.avatar_url,
            "country": profile.country
        }

        self.db.profiles.update_one(
            {"_id": profile.id},
            {"$set": document}
        )
        logger.info(f"Profile {profile.id} updated")

    def find_by_email(self, email: str) -> Optional[Profile]:
        profile_document = self.db.profiles.find_one({"email": email})

        if profile_document is not None:
            logger.debug(f"Found profile for email: {email}")
            logger.debug(f"Profile name: {profile_document.get('first_name')} {profile_document.get('last_name')}")

            return Profile(
                _id=profile_document["_id"],
                contact=Contact(
                    contact=f"{profile_document["username"]} <{profile_document["email"]}>",
                ),
                full_name=FullName.create(profile_document["first_name"], profile_document["last_name"]),
                password_hash=profile_document["password_hash"],
                initial_level=profile_document["initial_level"],
                language=profile_document["language"],
                bio=profile_document["bio"],
                avatar_url=profile_document["avatar_url"],
                country=profile_document["country"]
            )

        return None