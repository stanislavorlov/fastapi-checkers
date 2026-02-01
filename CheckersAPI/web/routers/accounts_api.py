import logging
from typing import Annotated
from fastapi import APIRouter, HTTPException, status, Request, Depends
from application.mediator import Mediator
from application.requests.register_profile import RegisterProfileRequest
from application.requests.create_player import CreatePlayerRequest
from domain.player.player_type import PlayerType
from web.client_helper import get_ip_info
from web.dependencies import get_mediator, get_player_repository, get_profile_repository
from web.models import CreateAccountDto, ProfileDto
from application.requests.update_profile import UpdateProfileRequest
from web.token_helper import oauth2_scheme, get_current_user
from infrastructure.repositories.profile_repository import ProfileRepository
from infrastructure.repositories.player_repository import PlayerRepository

router = APIRouter(
    prefix="/api",
    tags=["accounts"],
)

@router.post("/register")
async def register_account(
        request: Request,
        create_account: CreateAccountDto,
        mediator: Annotated[Mediator, Depends(get_mediator)]
):
    try:
        ip = request.headers.get("x-forwarded-for", request.client.host)
        # In case of multiple IPs in header, take the first
        if "," in ip:
            ip = ip.split(",")[0].strip()

        client_info_dict = get_ip_info(ip)

        language = client_info_dict.get("languages", "en,").split(",")[0]
        country = client_info_dict.get("country_code", "")

        register_request = RegisterProfileRequest(
            email=create_account.email,
            password=create_account.password,
            first_name=create_account.first_name,
            last_name=create_account.last_name,
            level=create_account.level,
            language=language,
            country=country
        )
        
        profile_id = await mediator.send(register_request)

        create_player = CreatePlayerRequest(
            type=PlayerType.ACCOUNT,
            profile_id=profile_id,
            player_level=create_account.level
        )

        await mediator.send(create_player)

        return {"status": "ok"}
    except Exception as e:
        logging.exception("error occurred during registration", exc_info=e)

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
        )

@router.get("/profile", response_model=ProfileDto)
async def get_profile(
    token: Annotated[str, Depends(oauth2_scheme)],
    profile_repo: Annotated[ProfileRepository, Depends(get_profile_repository)],
    player_repo: Annotated[PlayerRepository, Depends(get_player_repository)]
):
    current_user = await get_current_user(profile_repo, player_repo, token)
    if current_user.anonymous:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Guests don't have a profile")
    
    player = player_repo.get_by_id(current_user.player_id)
    profile = profile_repo.get(str(player.profile_id))
    
    return ProfileDto(
        email=profile.contact.email,
        username=profile.contact.username,
        first_name=profile.full_name.first.value if profile.full_name else "",
        last_name=profile.full_name.last.value if profile.full_name else "",
        language=profile.language or "",
        bio=profile.bio or "",
        avatar_url=profile.avatar_url or "",
        country=profile.country or ""
    )

@router.put("/profile")
async def update_profile(
    profile_dto: ProfileDto,
    token: Annotated[str, Depends(oauth2_scheme)],
    mediator: Annotated[Mediator, Depends(get_mediator)],
    profile_repo: Annotated[ProfileRepository, Depends(get_profile_repository)],
    player_repo: Annotated[PlayerRepository, Depends(get_player_repository)]
):
    current_user = await get_current_user(profile_repo, player_repo, token)
    if current_user.anonymous:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Guests cannot update profile")
    
    player = player_repo.get_by_id(current_user.player_id)
    
    update_request = UpdateProfileRequest(
        profile_id=str(player.profile_id),
        **profile_dto.model_dump()
    )
    
    success = await mediator.send(update_request)
    if not success:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to update profile")
    
    return {"status": "ok"}

@router.get("/client_info")
async def client_info(request: Request):
    ip = request.headers.get("x-forwarded-for", request.client.host)
    # In case of multiple IPs in header, take the first
    if "," in ip:
        ip = ip.split(",")[0].strip()

    return get_ip_info(ip)