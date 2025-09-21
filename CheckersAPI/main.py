import json
from collections import defaultdict
from contextlib import asynccontextmanager
from bson import ObjectId
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from starlette.websockets import WebSocket, WebSocketDisconnect
from web.history_dto import HistoryDto
from web.game_dto import GameDto
from infrastructure.database import history_collection
from infrastructure.event_parser import EventParser
from application.handlers import EventHandler
from infrastructure.database import game_collection
from infrastructure.schemas import list_games
from infrastructure.documents import Game

class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, list[WebSocket]] = defaultdict(list)

    async def connect(self, game_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[game_id].append(websocket)

        for w in self.active_connections[game_id]:
            print(w.application_state)

    async def disconnect(self, game_id: str, websocket: WebSocket):
        print('disconnect', game_id, websocket)
        self.active_connections[game_id].remove(websocket)

    async def broadcast(self, game_id: str, message: str):
        if game_id in self.active_connections:
            for websocket in self.active_connections[game_id]:
                await websocket.send_text(message)

    async def close_all(self):
        print(self.active_connections)
        for idx, game_id in enumerate(self.active_connections):
            print(idx, game_id)
            for ws in self.active_connections[game_id]:
                await ws.close()
            self.active_connections[game_id].clear()

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

    history_dto = []
    for history in history:
        history_dto.append(HistoryDto(history))

    return GameDto(game_id, game['name'], game['started'], history_dto)

@app.post("/api/")
async def post_game(game: Game):
    inserted = game_collection.insert_one(dict(game))

    return str(inserted.inserted_id)

@app.put("/api/{id}")
async def put_game(id: str, game: Game):
    game_collection.find_and_modify({"_id": ObjectId(id)}, {"$set":dict(game)})

    # ToDo: return

@app.delete("/api/{id}")
async def delete_game(id: str):
    game_collection.find_one_and_delete({"_id": ObjectId(id)})

@app.websocket("/ws/{game_id}")
async def websocket_endpoint(websocket: WebSocket, game_id: str):
    await manager.connect(game_id, websocket)
    try:
        while True:
            message_text = await websocket.receive_text()

            print(f"message received: {message_text}")

            try:
                game_event = EventParser().parse(message_text)
                handler = EventHandler(game_id)
                handler.handle(game_event)

            except json.decoder.JSONDecodeError:
                print('Error decoding JSON')

            # ToDo: validate per current game board
            await manager.broadcast(game_id, message_text)

    except WebSocketDisconnect:
        await manager.disconnect(game_id, websocket)
