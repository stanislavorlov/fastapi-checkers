from collections import defaultdict
from bson import ObjectId
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from starlette.websockets import WebSocket, WebSocketDisconnect
from database import collection_name
from schemas import list_games
from games import Game

app = FastAPI()

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

class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, list[WebSocket]] = defaultdict(list)

    async def connect(self, game_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[game_id].append(websocket)

    async def disconnect(self, game_id: str, websocket: WebSocket):
        self.active_connections[game_id].remove(websocket)

    async def broadcast(self, game_id: str, message: str):
        if game_id in self.active_connections:
            for websocket in self.active_connections[game_id]:
                await websocket.send_text(message)

manager = ConnectionManager()

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

@app.websocket("/ws/{game_id}")
async def websocket_endpoint(websocket: WebSocket, game_id: str):
    await manager.connect(game_id, websocket)
    try:
        while True:
            data = await websocket.receive_text()

            await manager.broadcast(game_id, data)
    except WebSocketDisconnect:
        await manager.disconnect(game_id, websocket)
