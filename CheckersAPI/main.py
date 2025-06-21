from bson import ObjectId
from fastapi import FastAPI
from database import collection_name
from schemas import list_games
from games import Game

app = FastAPI()

@app.get('/')
async def get_games():
    games = list_games(collection_name.find())

    return games

@app.post("/")
async def post_game(game: Game):
    collection_name.insert_one(dict(game))

@app.put("/{id}")
async def put_game(id: str, game: Game):
    collection_name.find_and_modify({"_id": ObjectId(id)}, {"$set":dict(game)})

@app.delete("/{id}")
async def delete_game(id: str):
    collection_name.find_one_and_delete({"_id": ObjectId(id)})