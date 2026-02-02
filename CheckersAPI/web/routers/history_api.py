import logging
from typing import Annotated
from fastapi import APIRouter, Request, Depends
from application.mediator import Mediator
from application.requests.resolve_player import ResolvePlayerRequest
from application.requests.retrieve_game_history import RetrieveGameHistoryRequest
from application.requests.retrieve_player_history import RetrievePlayerHistoryRequest
from infrastructure.mappers import list_games
from web.dependencies import get_mediator

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/history",
    tags=["history"]
)

@router.get("/")
async def player_history(
    request: Request,
    mediator: Annotated[Mediator, Depends(get_mediator)]
):
    resolve_request = ResolvePlayerRequest(
        auth_header=request.headers.get("Authorization"),
        client_host=request.client.host if request.client else "unknown",
        user_agent=request.headers.get("User-Agent", "unknown")
    )
    player_id = await mediator.send(resolve_request)

    history_request = RetrievePlayerHistoryRequest(
        player_id=player_id
    )

    history = await mediator.send(history_request)

    return list_games(history)

@router.get("/{game_id}")
async def game_history(
    request: Request,
    game_id: str,
    mediator: Annotated[Mediator, Depends(get_mediator)]
):
    history_request = RetrieveGameHistoryRequest(
        game_id=game_id
    )

    history = await mediator.send(history_request)

    return history