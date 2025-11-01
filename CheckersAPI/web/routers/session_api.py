from typing import Annotated
from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from domain.profile.profile import Profile
from infrastructure.repositories.profile_repository import ProfileRepository
from web.dependencies import get_profile_repository
from web.token_helper import verify_password, create_access_token, get_current_user, oauth2_scheme
from web.web_helper import parse_accept_language

router = APIRouter(
    prefix="/api",
    tags=["sessions"],
)

@router.post("/token")
async def login(
    request: Request,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
):
    client_host = request.client.host
    accept_language = request.headers.get("accept-language", "")

    # Parse and get the top preferred language
    create_account.language = parse_accept_language(accept_language)  # "en"

    user_dict = account_collection.find_one({"email": form_data.username})
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

    # ToDo: SessionService -> create session

    # ToDo: store token in database
    access_token = create_access_token(
        user_dict['user_id'],
        f"{user_dict['first_name']} {user_dict['last_name']}",
        user_dict['email'],
        'user')

    return access_token

@router.post("/guest-token")
async def guest_token():
    guest_id = str(ObjectId())

    # ToDo: SessionService -> create session

    # ToDo:  use domain logic for this
    token = create_access_token(
        guest_id,
        f'Guest Player {guest_id}',
        f'guest_player_{guest_id}@email.com',
        'guest')

    return token

# async def get_current_active_user(
#     current_user: Annotated[User, Depends(get_current_user)],
# ):
#
#     return current_user

@router.get("/users/me")
async def read_users_me(
    token: str = Depends(oauth2_scheme),
    profile_repo: ProfileRepository = Depends(get_profile_repository)
):
    return await get_current_user(token=token, profile_repository=profile_repo)

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