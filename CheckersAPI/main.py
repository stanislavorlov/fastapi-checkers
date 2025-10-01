import json
from contextlib import asynccontextmanager
from bson import ObjectId
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from starlette.websockets import WebSocket, WebSocketDisconnect
from infrastructure.connnection_manager import ConnectionManager
from infrastructure.database import history_collection, game_collection, player_collection
from infrastructure.event_parser import EventParser
from application.handlers import EventHandler
from infrastructure.schemas import list_games, individual_game
from web.game_dto import WriteGameDto


@asynccontextmanager
async def lifespan(app: FastAPI):
    # App startup
    print("🚀 App started")
    yield
    # App shutdown
    print("🛑 Shutting down. Closing all WebSocket connections...")
    await manager.close_all()

app = FastAPI(lifespan=lifespan)

origins = [
    'http://localhost:4200'
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*']
)

manager = ConnectionManager()

@app.get('/api/')
async def get_games():
    games = list_games(game_collection.find())

    return games

@app.get('/api/{game_id}')
async def get_game(game_id: str):
    game = game_collection.find_one({'_id': ObjectId(game_id)})
    history = history_collection.find({ 'game_id': game_id })

    return individual_game(game, history)

@app.post("/api/")
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

@app.websocket("/ws/{game_id}")
async def websocket_endpoint(websocket: WebSocket, game_id: str):
    await manager.connect(game_id, websocket)
    try:
        while True:
            user_actions = await websocket.receive_text()

            print(f"message received: {user_actions}")

            try:
                game_events = EventParser().parse(user_actions)
                handler = EventHandler(game_id, manager)
                await handler.handle(game_events)

            except json.decoder.JSONDecodeError:
                print('Error decoding JSON')

    except WebSocketDisconnect:
        await manager.disconnect(game_id, websocket)
