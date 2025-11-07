import logging
from typing import Annotated
from fastapi import APIRouter, HTTPException, status, Request, Depends
from application.handlers.register_profile_handler import RegisterProfileHandler
from web.client_helper import get_ip_info
from web.dependencies import get_register_profile_handler
from web.models import CreateAccountDto

router = APIRouter(
    prefix="/api",
    tags=["accounts"],
)

@router.post("/register")
async def register_account(
        request: Request,
        create_account: CreateAccountDto,
        handler: Annotated[RegisterProfileHandler, Depends(get_register_profile_handler)]
):
    try:
        ip = request.headers.get("x-forwarded-for", request.client.host)
        # In case of multiple IPs in header, take the first
        if "," in ip:
            ip = ip.split(",")[0].strip()

        client_info_dict = get_ip_info(ip)

        create_account.language = client_info_dict.get("languages", "en,").split(",")[0]
        create_account.country = client_info_dict.get("country_code", "")

        handler.handle(create_account)

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