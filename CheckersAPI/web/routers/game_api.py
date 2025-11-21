from typing import Annotated
from bson import ObjectId
from fastapi import APIRouter, Depends, Request, HTTPException
from infrastructure.repositories.game_repository import GameRepository
from infrastructure.mappers import individual_game
from web.dependencies import get_game_repository
from web.models import RequestComputerGameDto, RequestOnlineGameDto
from web.token_helper import get_current_user

router = APIRouter(
    prefix="/api/games",
    tags=["games"]
)

@router.get('/{game_id}')
async def get_game(
        game_id: str,
        repository: Annotated[GameRepository, Depends(get_game_repository)]
):
    return await repository.fetch(game_id)

# @router.post("/online")
# async def request_online_game(
#         request_dto: RequestOnlineGameDto,
#         current_user: Annotated[UserSchema, Depends(get_current_user)]):
#     # ToDo: player request a game
#     # System starts MatchMaking algorithm
#     # Once found, player receives a notification and after than game is created
#
#     # ToDo: player should be authenticated with anonymous token by default
#     match_collection.insert_one()
#
#     # MongoDB change stream
#
#     def watch_changes():
#         pipeline = [{"$match": {"operationType": "insert"}}]
#         with game_collection.watch(pipeline, full_document="updateLookup") as stream:
#             print("Change stream started")
#             for change in stream:
#                 doc = change["fullDocument"]
#                 message = {}
#
#                 # ToDo: broadcast message via WebSockets
#
#     # ToDo: should be run in a separate thread in main -> lifespan
#     # thread = Thread(target=watch_changes, daemon=True)
#     # thread.start()
#
# @router.post("/computer")
# async def request_computer_game(
#         request_dto: RequestComputerGameDto,
#         current_user: Annotated[UserSchema, Depends(get_current_user)]):
#     game = dict(game_dto)
#
#     # ToDo: player should be authenticated with anonymous token by default
#     player = game_dto.players[0]
#
#     inserted = game_collection.insert_one(game)
#
#     upsert_player(game_dto.dark_player)
#     upsert_player(game_dto.light_player)
#
#     return str(inserted.inserted_id)
#
# def upsert_player(player_id: str):
#     if player_id != "AI":
#         user_collection.find_one_and_update(
#             filter={'player_id': player_id},
#             update={'$set': {'player_id': player_id}},
#             upsert=True)
#
# @app.put("/api/{id}")
# async def put_game(id: str, game: GameDto):
#     game_collection.find_and_modify({"_id": ObjectId(id)}, {"$set":dict(game)})
#
#     # ToDo: return
#
from application.requests.create_player import CreatePlayerRequest
from domain.player.player_type import PlayerType
from web.token_helper import decode_access_token
from infrastructure.repositories.matching_repository import MatchingRepository
from infrastructure.repositories.game_repository import GameRepository
from web.dependencies import get_matching_repository, get_create_player_handler, get_game_repository
from web.models import RequestGameResponse
from application.handlers.create_player_handler import CreatePlayerHandler

@router.post("/request_game", response_model=RequestGameResponse)
async def request_game(
        request: Request,
        matching_repository: Annotated[MatchingRepository, Depends(get_matching_repository)],
        player_handler: Annotated[CreatePlayerHandler, Depends(get_create_player_handler)]
):
    player_id = ""
    
    auth_header = request.headers.get("Authorization")
    if auth_header:
        try:
            token = auth_header.split(" ")[1]
            payload = decode_access_token(token)
            player_id = payload.sub
        except Exception:
            # If token is invalid, treat as guest? Or raise error?
            # For now, let's assume if they try to auth and fail, it's an error.
            # But if they just don't send it, it's guest.
            # However, to be safe and follow "Otherwise, create a Player document for un-authorized user",
            # we can fall back to guest creation if auth fails, or strictly require valid auth if header is present.
            # Let's strictly require valid auth if header is present to avoid confusion.
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    else:
        # Create guest player
        create_player_request = CreatePlayerRequest(
            type=PlayerType.GUEST,
            player_level="1", # Default level for guest
            profile_id=None
        )
        player_id = player_handler.handle(create_player_request)

    # Add to matching queue
    # ToDo: get region and rating from player or request?
    # For now using defaults
    matching_repository.add_to_queue(player_id=player_id, region="EU", rating=1000)

    return RequestGameResponse(player_id=player_id, status="waiting")