from infrastructure.database import user_collection
from infrastructure.schemas import user_profile, individual_user


class UserRepository:

    def get_user_by_id(self, user_id: int):
        user_dict = user_collection.find_one({"user_id": user_id})

        return individual_user(user_dict) if user_dict else None

    def get_user_profile(self, user_id):
        pipeline = [
            {"$match": {"user_id": user_id}},
            {
                "$lookup": {
                    "from": "players",  # collection to join
                    "let": {"pid": {"$toObjectId": "$player_id"}},  # convert string → ObjectId
                    "pipeline": [
                        {"$match": {"$expr": {"$eq": ["$_id", "$$pid"]}}}
                    ],
                    "as": "player"  # output field name
                }
            },
            {
                "$unwind": "$player"  # optional: flatten list of joined players
            }
        ]

        result = list(user_collection.aggregate(pipeline))

        return user_profile(result[0]) if len(result) > 0 else None