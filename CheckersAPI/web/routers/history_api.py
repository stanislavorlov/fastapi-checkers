import logging
from fastapi import APIRouter, Request

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/history",
    tags=["history"]
)

@router.get("/")
async def get_history(
    request: Request
):
    return "history of played games"

@router.get("/{game_id}")
async def get_game_history(
    request: Request,
    game_id: str
):
    return "game history of played game id: {}".format(game_id)