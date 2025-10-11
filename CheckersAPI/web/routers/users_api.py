import hashlib
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from infrastructure.database import user_collection, player_collection
from infrastructure.documents import User, Player
from web.models import CreateUser, AccessTokenData
from web.player_helper import detect_region, initial_rank, initial_stats
from web.user_helper import hash_password, nanoid, verify_password, create_access_token, get_current_user

router = APIRouter(
    prefix="/api",
    tags=["users"],
)

@router.post("/register")
async def register_user(create_user: CreateUser):
    try:
        user = User(
            first_name=create_user.first_name,
            last_name=create_user.last_name,
            country=create_user.country,
            user_id=nanoid(10),
            email=create_user.email,
            password_hash=hash_password(create_user.password),
        )
        user_collection.insert_one(dict(user))

        player = Player(
            user_id=user.user_id,
            is_anonymous=False,
            region=detect_region(user.country),
            rank=initial_rank(create_user.level),
            stats=initial_stats()
        )
        player_collection.insert_one(dict(player))

        return {"status": "ok"}
    except:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
        )

@router.post("/token")
async def login_user(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user_dict = user_collection.find_one({"email": form_data.username})
    if not user_dict:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    hashed_password = user_dict['password_hash']

    if not verify_password(form_data.password, hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )

    access_token = create_access_token(
        data=AccessTokenData(
            sub=user_dict['user_id'],
            name=f"{user_dict['first_name']} {user_dict['last_name']}",
            preferred_username=user_dict['email'],
        ),
        token_type='user'
    )

    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/guest-token")
async def guest_token():
    # guest_id = f"guest_{uuid.uuid4().hex[:6]}"
    # payload = {
    #     "sub": guest_id,
    #     "type": "guest",
    #     "iat": datetime.utcnow(),
    #     "exp": datetime.utcnow() + timedelta(days=1)  # 24-hour token
    # }
    # token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    token = create_access_token(
        data=AccessTokenData(
            sub='',
            preferred_username='',
            name=''
        ),
        token_type='guest'
    )

    return {"access_token": token, "token_type": "bearer"}

async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
):
    #if current_user.disabled:
    #    raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

@router.get("/users/me")
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_active_user)]
):
    return current_user

# @router.get("/users/ip")
# def get_current_user_ip(request: Request):
#     # ToDo: better to generate some deviceId on the client side
#     ip = request.headers.get("x-forwarded-for") or request.client.host
#     agent = request.headers.get("user-agent", "unknown")
#
#     unique_string = f"{ip}:{agent}"
#     fingerprint = hashlib.sha256(unique_string.encode()).hexdigest()
#
#     return {"ip": ip, "agent": agent, "fingerprint": fingerprint}