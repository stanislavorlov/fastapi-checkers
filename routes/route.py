from bson import ObjectId
from fastapi import APIRouter

from config.database import collection_name
from models.games import Game
from schema.schemas import list_games

router = APIRouter()

@router.get('/')
async def get_games():
    games = list_games(collection_name.find())

    return games

@router.post("/")
async def post_game(game: Game):
    collection_name.insert_one(dict(game))

@router.put("/{id}")
async def put_game(id: str, game: Game):
    collection_name.find_and_modify({"_id": ObjectId(id)}, {"$set":dict(game)})

@router.delete("/{id}")
async def delete_game(id: str):
    collection_name.find_one_and_delete({"_id": ObjectId(id)})