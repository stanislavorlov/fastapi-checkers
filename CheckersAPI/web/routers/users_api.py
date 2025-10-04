from datetime import timedelta
from typing import Annotated
import jwt
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jwt import InvalidTokenError
from infrastructure.database import player_collection
from infrastructure.documents import Player
from infrastructure.schemas import single_player
from web.models import CreateUser
from web.user_helper import hash_password, nanoid, verify_password, ACCESS_TOKEN_EXPIRE_MINUTES, create_access_token, \
    SECRET_KEY, ALGORITHM

router = APIRouter(
    prefix="/api",
    tags=["users"],
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/token")

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
async def login_user(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
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

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": form_data.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
        #token_data = TokenData(username=username)
    except InvalidTokenError:
        raise credentials_exception
    #user = get_user(fake_users_db, username=username)
    player_dict = player_collection.find_one({"username": username})
    if player_dict is None:
        raise credentials_exception

    return single_player(player_dict)

async def get_current_active_user(
    current_user: Annotated[Player, Depends(get_current_user)],
):
    #if current_user.disabled:
    #    raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

@router.get("/users/me")
async def read_users_me(
    current_user: Annotated[Player, Depends(get_current_active_user)]
):
    return current_user