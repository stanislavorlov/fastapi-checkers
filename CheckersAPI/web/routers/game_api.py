from typing import Annotated
from bson import ObjectId
from fastapi import APIRouter, Depends
from infrastructure.database import game_collection, history_collection, user_collection, match_collection
from infrastructure.documents import UserSchema
from infrastructure.schemas import list_games, individual_game
from web.models import RequestComputerGameDto, RequestOnlineGameDto
from web.user_helper import get_current_user

router = APIRouter(
    prefix="/api/games",
    tags=["games"]
)

@router.get('/')
async def get_games():
    games = list_games(game_collection.find())

    return games

@router.get('/{game_id}')
async def get_game(game_id: str):
    try:
        game = game_collection.find_one({'_id': ObjectId(game_id)})
        history = history_collection.find({ 'game_id': game_id })

        return individual_game(game, history)
    except Exception as e:
        return str(e)

@router.post("/online")
async def request_online_game(
        request_dto: RequestOnlineGameDto,
        current_user: Annotated[UserSchema, Depends(get_current_user)]):
    # ToDo: player request a game
    # System starts MatchMaking algorithm
    # Once found, player receives a notification and after than game is created

    # ToDo: player should be authenticated with anonymous token by default
    match_collection.insert_one()

    # MongoDB change stream

    def watch_changes():
        pipeline = [{"$match": {"operationType": "insert"}}]
        with game_collection.watch(pipeline, full_document="updateLookup") as stream:
            print("Change stream started")
            for change in stream:
                doc = change["fullDocument"]
                message = {}

                # ToDo: broadcast message via WebSockets

    # ToDo: should be run in a separate thread in main -> lifespan
    # thread = Thread(target=watch_changes, daemon=True)
    # thread.start()

@router.post("/computer")
async def request_computer_game(
        request_dto: RequestComputerGameDto,
        current_user: Annotated[UserSchema, Depends(get_current_user)]):
    game = dict(game_dto)

    # ToDo: player should be authenticated with anonymous token by default
    player = game_dto.players[0]

    inserted = game_collection.insert_one(game)

    upsert_player(game_dto.dark_player)
    upsert_player(game_dto.light_player)

    return str(inserted.inserted_id)

def upsert_player(player_id: str):
    if player_id != "AI":
        user_collection.find_one_and_update(
            filter={'player_id': player_id},
            update={'$set': {'player_id': player_id}},
            upsert=True)

# @app.put("/api/{id}")
# async def put_game(id: str, game: GameDto):
#     game_collection.find_and_modify({"_id": ObjectId(id)}, {"$set":dict(game)})
#
#     # ToDo: return
#
# @app.delete("/api/{id}")
# async def delete_game(id: str):
#     game_collection.find_one_and_delete({"_id": ObjectId(id)})