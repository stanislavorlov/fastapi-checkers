from collections import defaultdict
from contextlib import asynccontextmanager

from bson import ObjectId
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from starlette.websockets import WebSocket, WebSocketDisconnect
from database import collection_name
from schemas import list_games
from games import Game

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
    games = list_games(collection_name.find())

    return games

@app.post("/api/")
async def post_game(game: Game):
    inserted = collection_name.insert_one(dict(game))

    return str(inserted.inserted_id)

@app.put("/api/{id}")
async def put_game(id: str, game: Game):
    collection_name.find_and_modify({"_id": ObjectId(id)}, {"$set":dict(game)})

    # ToDo: return

@app.delete("/api/{id}")
async def delete_game(id: str):
    collection_name.find_one_and_delete({"_id": ObjectId(id)})

@app.websocket("/ws/{game_id}")
async def websocket_endpoint(websocket: WebSocket, game_id: str):
    await manager.connect(game_id, websocket)
    try:
        while True:
            data = await websocket.receive_text()

            print(data)

            await manager.broadcast(game_id, data)
    except WebSocketDisconnect:
        await manager.disconnect(game_id, websocket)
