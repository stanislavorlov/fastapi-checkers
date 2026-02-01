import logging
from typing import Annotated
from fastapi import APIRouter, Depends, Request, HTTPException
from application.mediator import Mediator
from application.requests.resolve_player import ResolvePlayerRequest
from application.requests.start_computer_game import StartComputerGameRequest
from application.requests.join_queue import JoinQueueRequest
from application.requests.move import MoveRequest
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
        mediator: Annotated[Mediator, Depends(get_mediator)]
):
    game = repository.fetch(game_id)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")

    logger.debug("Trigger AI move check to ensure AI moves first if it's its turn")
    # For compatibility, we still want to trigger AI move if it's its turn
    # This might be slightly awkward with Mediator if we only want to call trigger_ai_move
    # But since MoveHandler is the one having this method, we can either:
    # 1. Keep depending on MoveHandler for this specific call
    # 2. Add a TriggerAiMoveRequest
    
    # Let's see MoveHandler again. 
    # Actually, we can just fetch the handler from mediator if we really need a specific method, 
    # but that's against the pattern.
    
    # Better: StartComputerGameHandler or a new specialized handler should handle this.
    # For now, let's just use MoveHandler directly for this specific legacy-ish call, 
    # or just let the client (WS) trigger it. 
    # Actually, the GET endpoint triggering an AI move is a bit weird anyway.
    
    # Let's check MoveHandler. 
    from application.handlers.websocket.move_handler import MoveHandler
    move_handler = mediator._handlers[MoveRequest] # A bit of a hack but avoids adding more requests for now
    await move_handler.trigger_ai_move(game)
        
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