import logging
from typing import Annotated
from bson import ObjectId
from fastapi import APIRouter, Depends, Request, HTTPException

from infrastructure.documents import PyObjectId, PlayerType
from infrastructure.repositories.game_repository import GameRepository
from infrastructure.repositories.player_repository import PlayerRepository
from infrastructure.repositories.matching_repository import MatchingRepository
from web.dependencies import (
    get_game_repository,
    get_player_repository,
    get_matching_repository,
    get_resolve_guest_player_handler,
    get_game_event_handler, get_create_player_handler
)
from application.handlers.game_event_handler import GameEventHandler
from application.handlers.resolve_guest_player_handler import ResolveGuestPlayerHandler
from web.models import RequestGameResponse, ReadGameDto, StartComputerGameDto
from infrastructure.mappers import individual_game
from web.token_helper import decode_access_token
from application.handlers.create_player_handler import CreatePlayerHandler
from application.requests.create_player import CreatePlayerRequest

from domain.player.player import Player
from domain.player.player_type import PlayerType as DomainPlayerType
from domain.player.display_name import DisplayName
from domain.player.rank import Rank
from domain.player.stats import PlayerStats
from domain.game.game import Game
from domain.game.game_mode import GameMode
from domain.side import Side
from datetime import datetime, timezone

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
        repository: Annotated[GameRepository, Depends(get_game_repository)],
        player_repository: Annotated[PlayerRepository, Depends(get_player_repository)],
        player_handler: Annotated[CreatePlayerHandler, Depends(get_create_player_handler)],
        resolve_guest_player_handler: Annotated[ResolveGuestPlayerHandler, Depends(get_resolve_guest_player_handler)],
        handler: Annotated[GameEventHandler, Depends(get_game_event_handler)]
):
    player_id = await _get_or_create_player_id(request, player_handler, resolve_guest_player_handler)
    player = player_repository.get_by_id(player_id)
    
    # Create AI bot player object
    ai_bot = Player(
        display_name=DisplayName(display_name="AI Bot"),
        _type=DomainPlayerType.AI,
        _rank=Rank.intermediate(),
        _stats=PlayerStats.create_empty()
    )
    
    player_side = Side.Light if data.singleSide == "red" else Side.Dark
    ai_side = Side.Dark if player_side == Side.Light else Side.Light

    new_game = Game(
        created_at=datetime.now(timezone.utc),
        mode=GameMode.PVE,
        players={
            Side.Light : ai_bot if ai_side == Side.Light else player,
            Side.Dark : ai_bot if ai_side == Side.Dark else player
        },
        history=[],
        result={}
    )
    
    game_id = repository.create(new_game)
    
    # Set the ID on the domain object so trigger_ai_move can use it if needed
    new_game.id = PyObjectId(game_id)
    
    # Trigger AI move immediately on creation
    await handler.trigger_ai_move(new_game)
    
    return str(game_id)

@router.post("/online", response_model=RequestGameResponse)
async def request_online_game(
        request: Request,
        matching_repository: Annotated[MatchingRepository, Depends(get_matching_repository)],
        player_handler: Annotated[CreatePlayerHandler, Depends(get_create_player_handler)],
        resolve_guest_player_handler: Annotated[ResolveGuestPlayerHandler, Depends(get_resolve_guest_player_handler)]
):
    player_id = await _get_or_create_player_id(request, player_handler, resolve_guest_player_handler)
    
    # Add to matching queue
    matching_repository.add_to_queue(player_id=player_id, region="EU", rating=1000)

    return RequestGameResponse(player_id=player_id, status="waiting")

async def _get_or_create_player_id(
    request: Request, 
    player_handler: CreatePlayerHandler,
    resolve_guest_player_handler: ResolveGuestPlayerHandler
) -> str:
    auth_header = request.headers.get("Authorization")
    if auth_header:
        try:
            token = auth_header.split(" ")[1]
            payload = decode_access_token(token)
            return payload.sub
        except Exception:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    
    # Resolve guest player idempotently
    client_host = request.client.host if request.client else "unknown"
    agent = request.headers.get("User-Agent", "unknown")
    
    return resolve_guest_player_handler.handle(client_host, agent)