from domain.users.user import User
from infrastructure.documents import UserSchema


def domain_to_schema(user: User, player_id: str) -> UserSchema:
    return UserSchema.model_validate({
        **user.__dict__,
        "player_id": player_id
    })