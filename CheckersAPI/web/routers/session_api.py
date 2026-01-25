from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from application.handlers.retrieve_token_handler import RetrieveTokenHandler
from application.requests.retrieve_token import RetrieveGuestToken, RetrieveProfileToken
from infrastructure.repositories.profile_repository import ProfileRepository
from infrastructure.repositories.player_repository import PlayerRepository
from web.dependencies import get_profile_repository, get_retrieve_token_handler, get_player_repository
from web.token_helper import get_current_user, oauth2_scheme

router = APIRouter(
    prefix="/api",
    tags=["sessions"],
)

@router.post("/token")
async def login(
    request: Request,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    token_handler: Annotated[RetrieveTokenHandler, Depends(get_retrieve_token_handler)]
):
    retrieve_token = RetrieveProfileToken(
        client_host=request.client.host,
        accept_language=request.headers.get("accept-language", ""),
        username=form_data.username,
        password=form_data.password,
        agent=request.headers.get("user-agent", ""),
    )

    print(f"Headers: {request.headers}")
    access_token = token_handler.handle(retrieve_token)

    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    return access_token

@router.post("/guest-token")
async def guest_token(
    request: Request,
    token_handler: Annotated[RetrieveTokenHandler, Depends(get_retrieve_token_handler)],
):
    retrieve_token = RetrieveGuestToken(
        client_host=request.client.host,
        accept_language=request.headers.get("accept-language", ""),
        agent=request.headers.get("user-agent", ""),
    )

    print(f"Headers: {request.headers}")
    print(f"user agent: {retrieve_token.agent}")

    access_token = token_handler.handle(retrieve_token)

    return access_token

@router.get("/users/me")
async def read_users_me(
    token: str = Depends(oauth2_scheme),
    profile_repo: ProfileRepository = Depends(get_profile_repository),
    player_repo: PlayerRepository = Depends(get_player_repository)
):
    return await get_current_user(token=token, profile_repository=profile_repo, player_repository=player_repo)

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