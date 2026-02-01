from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from application.mediator import Mediator
from application.requests.retrieve_token import RetrieveGuestToken, RetrieveProfileToken
from infrastructure.repositories.profile_repository import ProfileRepository
from infrastructure.repositories.player_repository import PlayerRepository
from web.dependencies import get_profile_repository, get_mediator, get_player_repository
from web.models import RefreshTokenDto
from web.token_helper import get_current_user, oauth2_scheme, decode_access_token, create_access_token, InvalidTokenError

router = APIRouter(
    prefix="/api",
    tags=["sessions"],
)

@router.post("/token")
async def login(
    request: Request,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    mediator: Annotated[Mediator, Depends(get_mediator)]
):
    retrieve_token = RetrieveProfileToken(
        client_host=request.client.host,
        accept_language=request.headers.get("accept-language", ""),
        username=form_data.username,
        password=form_data.password,
        agent=request.headers.get("user-agent", ""),
    )

    print(f"Headers: {request.headers}")
    access_token = await mediator.send(retrieve_token)

    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    return access_token

@router.post("/guest-token")
async def guest_token(
    request: Request,
    mediator: Annotated[Mediator, Depends(get_mediator)],
):
    retrieve_token = RetrieveGuestToken(
        client_host=request.client.host,
        accept_language=request.headers.get("accept-language", ""),
        agent=request.headers.get("user-agent", ""),
    )

    print(f"Headers: {request.headers}")
    print(f"user agent: {retrieve_token.agent}")

    access_token = await mediator.send(retrieve_token)

    return access_token

@router.post("/refresh")
async def refresh_token(
    refresh_data: RefreshTokenDto
):
    try:
        # Decode the refresh token using the shared helper
        # Since we use the same structure for both tokens, decode_access_token works
        payload = decode_access_token(refresh_data.refresh_token)
        
        # Issue a new pair of tokens
        new_tokens = create_access_token(
            player_id=payload.sub,
            name=payload.name,
            email=payload.preferred_username,
            access_type=payload.type
        )
        
        return new_tokens
    except InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid refresh token: {e}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Could not refresh token: {e}"
        )

@router.get("/users/me")
async def read_users_me(
    token: str = Depends(oauth2_scheme),
    profile_repo: ProfileRepository = Depends(get_profile_repository),
    player_repo: PlayerRepository = Depends(get_player_repository)
):
    return await get_current_user(token=token, profile_repository=profile_repo, player_repository=player_repo)