import logging
from typing import Annotated
from fastapi import APIRouter, HTTPException, status, Request, Depends
from application.handlers.register_profile_handler import RegisterProfileHandler
from web.dependencies import get_register_profile_handler
from web.models import CreateAccountDto
from web.web_helper import parse_accept_language

router = APIRouter(
    prefix="/api",
    tags=["accounts"],
)

logger = logging.getLogger("checkers_app")

@router.post("/register")
async def register_account(
        request: Request,
        create_account: CreateAccountDto,
        handler: Annotated[RegisterProfileHandler, Depends(get_register_profile_handler)]
):
    try:
        language = parse_accept_language(request.headers.get("Accept-Language", ""))
        create_account.language = language

        handler.handle(create_account)

        return {"status": "ok"}
    except Exception as e:
        print(e)
        logger.exception("error occurred during registration", exc_info=e)

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
        )