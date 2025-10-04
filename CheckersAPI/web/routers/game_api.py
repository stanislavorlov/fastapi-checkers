from bson import ObjectId
from infrastructure.database import game_collection, history_collection, player_collection
from infrastructure.schemas import list_games, individual_game
from web.models import WriteGameDto
from fastapi import APIRouter

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

@router.post("/")
async def post_game(game_dto: WriteGameDto):
    game = dict(game_dto)

    inserted = game_collection.insert_one(game)

    upsert_player(game_dto.dark_player)
    upsert_player(game_dto.light_player)

    return str(inserted.inserted_id)

def upsert_player(player_id: str):
    if player_id != "AI":
        player_collection.find_one_and_update(
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