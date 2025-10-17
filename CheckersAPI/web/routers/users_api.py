import logging
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from application.services.player_service import PlayerService
from infrastructure.database import user_collection
from infrastructure.documents import UserSchema
from web.models import CreateUserDto, AccessTokenData
from web.user_helper import verify_password, create_access_token, get_current_user

router = APIRouter(
    prefix="/api",
    tags=["users"],
)

logger = logging.getLogger("checkers_app")

@router.post("/register")
async def register_user(create_user: CreateUserDto):
    try:
        PlayerService.register_user(create_user)

        return {"status": "ok"}
    except Exception as e:
        print(e)
        logger.exception("error occurred during registration", exc_info=e)

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

    print('checking password')
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
            type='user'
        )
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
            name='',
            type='guest'
        )
    )

    return {"access_token": token, "token_type": "bearer"}

# async def get_current_active_user(
#     current_user: Annotated[User, Depends(get_current_user)],
# ):
#
#     return current_user

@router.get("/users/me")
async def read_users_me(
    current_user: Annotated[UserSchema, Depends(get_current_user)]
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