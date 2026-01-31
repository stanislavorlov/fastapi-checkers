import logging
from typing import Annotated
from fastapi import APIRouter, Depends, Request, HTTPException

from infrastructure.repositories.game_repository import GameRepository
from web.dependencies import (
    get_game_repository,
    get_game_event_handler,
    get_resolve_player_handler,
    get_start_computer_game_handler,
    get_join_queue_handler
)
from application.handlers.game_event_handler import GameEventHandler
from application.handlers.resolve_player_handler import ResolvePlayerHandler
from application.handlers.start_computer_game_handler import StartComputerGameHandler
from application.handlers.join_queue_handler import JoinQueueHandler
from web.models import RequestGameResponse, ReadGameDto, StartComputerGameDto
from infrastructure.mappers import individual_game

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/games",
    tags=["games"]
)

@router.get('/{game_id}', response_model=ReadGameDto)
async def get_game(
        game_id: str,
        repository: Annotated[GameRepository, Depends(get_game_repository)],
        handler: Annotated[GameEventHandler, Depends(get_game_event_handler)]
):
    game = repository.fetch(game_id)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")

    logger.debug("Trigger AI move check to ensure AI moves first if it's its turn")
    await handler.trigger_ai_move(game)
        
    return individual_game(game)

@router.post("/computer")
async def request_computer_game(
        request: Request,
        data: StartComputerGameDto,
        resolve_handler: Annotated[ResolvePlayerHandler, Depends(get_resolve_player_handler)],
        start_handler: Annotated[StartComputerGameHandler, Depends(get_start_computer_game_handler)]
):
    player_id = await resolve_handler.handle(request)
    game_id = await start_handler.handle(player_id, data.singleSide)
    
    return game_id

@router.post("/online", response_model=RequestGameResponse)
async def request_online_game(
        request: Request,
        resolve_handler: Annotated[ResolvePlayerHandler, Depends(get_resolve_player_handler)],
        join_handler: Annotated[JoinQueueHandler, Depends(get_join_queue_handler)]
):
    player_id = await resolve_handler.handle(request)
    await join_handler.handle(player_id)

    return RequestGameResponse(player_id=player_id, status="waiting")