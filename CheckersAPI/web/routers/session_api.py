from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from application.handlers.create_player_handler import CreatePlayerHandler
from application.handlers.guest_token_handler import GuestTokenHandler
from application.handlers.retrieve_token_handler import RetrieveTokenHandler
from application.requests.create_player import CreatePlayerRequest
from application.requests.retrieve_token import RetrieveToken
from domain.player.player_type import PlayerType
from infrastructure.repositories.profile_repository import ProfileRepository
from web.dependencies import get_profile_repository, get_retrieve_token_handler, get_create_player_handler, \
    get_guest_token_handler
from web.token_helper import get_current_user, oauth2_scheme

router = APIRouter(
    prefix="/api",
    tags=["sessions"],
)

@router.post("/token")
async def login(
    request: Request,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    token_handler: Annotated[RetrieveTokenHandler, Depends(get_retrieve_token_handler)],
    player_handler: Annotated[CreatePlayerHandler, Depends(get_create_player_handler)],
):
    retrieve_token = RetrieveToken(
        request.client.host,
        request.headers.get("accept-language", ""),
        form_data.username,
        form_data.password
    )

    access_token = token_handler.handle(retrieve_token)

    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    create_player = CreatePlayerRequest(
        type=PlayerType.ACCOUNT,
        profile_id=access_token.user_id,
        player_level=''
    )

    player_handler.handle(create_player)

    return access_token

@router.post("/guest-token")
async def guest_token(
    guest_token_handler: Annotated[GuestTokenHandler, Depends(get_guest_token_handler)],
    player_handler: Annotated[CreatePlayerHandler, Depends(get_create_player_handler)]
):
    create_player = CreatePlayerRequest(
        type=PlayerType.GUEST,
        player_level=''
    )

    player_handler.handle(create_player)

    access_token = guest_token_handler.handle()

    return access_token

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