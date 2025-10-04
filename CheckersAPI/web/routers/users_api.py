from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from infrastructure.database import player_collection
from infrastructure.documents import Player
from web.models import CreateUser
from web.user_helper import hash_password, nanoid

router = APIRouter(
    prefix="/api",
    tags=["users"],
)

@router.post("/register")
async def register_user(user: CreateUser):
    player = Player(
        first_name=user.first_name,
        last_name=user.last_name,
        country=user.country,
        player_id=nanoid(10),
        username=user.username,
        password_hash=hash_password(user.password),
    )

    player_collection.insert_one(dict(player))

    return {"status": "ok"}

@router.post("/token")
async def login_user(form_data: OAuth2PasswordRequestForm = Depends()):
    print(form_data.username, form_data.password)