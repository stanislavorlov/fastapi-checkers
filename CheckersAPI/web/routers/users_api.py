from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from infrastructure.database import player_collection
from infrastructure.documents import Player
from web.models import CreateUser
from web.user_helper import hash_password, nanoid, verify_password

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
    player_dict = player_collection.find_one({"username": form_data.username})
    if not player_dict:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    hashed_password = player_dict['password_hash']

    if not verify_password(form_data.password, hashed_password):
        print('password not match')
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )

    return {"access_token": form_data.username, "token_type": "bearer"}

@router.get("/users/me")
async def read_users_me():
    pass