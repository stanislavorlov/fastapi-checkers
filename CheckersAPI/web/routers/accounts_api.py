import logging
from typing import Annotated
from fastapi import APIRouter, HTTPException, status, Request, Depends
from application.mediator import Mediator
from application.requests.register_profile import RegisterProfileRequest
from application.requests.create_player import CreatePlayerRequest
from domain.player.player_type import PlayerType
from web.client_helper import get_ip_info
from web.dependencies import get_mediator
from web.models import CreateAccountDto

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

@router.get("/client_info")
async def client_info(request: Request):
    ip = request.headers.get("x-forwarded-for", request.client.host)
    # In case of multiple IPs in header, take the first
    if "," in ip:
        ip = ip.split(",")[0].strip()

    return get_ip_info(ip)