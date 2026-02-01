import logging
from typing import Annotated
from fastapi import APIRouter, Depends, Request, HTTPException
from application.mediator import Mediator
from application.requests.resolve_player import ResolvePlayerRequest
from application.requests.start_computer_game import StartComputerGameRequest
from application.requests.join_queue import JoinQueueRequest
from infrastructure.repositories.game_repository import GameRepository
from web.dependencies import (
    get_game_repository,
    get_mediator
)
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
):
    game = repository.fetch(game_id)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")

    return individual_game(game)

@router.post("/computer")
async def request_computer_game(
        request: Request,
        data: StartComputerGameDto,
        mediator: Annotated[Mediator, Depends(get_mediator)]
):
    resolve_request = ResolvePlayerRequest(
        auth_header=request.headers.get("Authorization"),
        client_host=request.client.host if request.client else "unknown",
        user_agent=request.headers.get("User-Agent", "unknown")
    )
    player_id = await mediator.send(resolve_request)
    
    start_request = StartComputerGameRequest(player_id=player_id, single_side=data.singleSide)
    game_id = await mediator.send(start_request)
    
    return game_id

@router.post("/online", response_model=RequestGameResponse)
async def request_online_game(
        request: Request,
        mediator: Annotated[Mediator, Depends(get_mediator)]
):
    resolve_request = ResolvePlayerRequest(
        auth_header=request.headers.get("Authorization"),
        client_host=request.client.host if request.client else "unknown",
        user_agent=request.headers.get("User-Agent", "unknown")
    )
    player_id = await mediator.send(resolve_request)
    
    join_request = JoinQueueRequest(player_id=player_id)
    await mediator.send(join_request)

    return RequestGameResponse(player_id=player_id, status="waiting")