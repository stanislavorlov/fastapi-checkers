import json
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from starlette.middleware.cors import CORSMiddleware
from starlette.websockets import WebSocket, WebSocketDisconnect
from infrastructure.connnection_manager import ConnectionManager
from infrastructure.event_parser import EventParser
from application.handlers import EventHandler
from web.routers import game_api


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

app.include_router(game_api.router)

manager = ConnectionManager()

def get_parser():
    return EventParser()

def get_handler(game_id: str):
    return EventHandler(game_id, manager)

async def message_loop(websocket: WebSocket, parser: EventParser, handler: EventHandler):
    while True:
        move_message = await websocket.receive_text()
        print(f"message received: {move_message}")

        try:
            player, pdn_move = parser.parse(move_message)
            await handler.handle(player, pdn_move)

        except json.decoder.JSONDecodeError:
            print("Error decoding JSON")
        except Exception as e:
            print(f"Unexpected error: {e}")

@app.websocket("/ws/{game_id}")
async def websocket_endpoint(
        websocket: WebSocket,
        game_id: str,
        parser: EventParser = Depends(get_parser),
        handler: EventHandler = Depends(get_handler)
):
    await manager.connect(game_id, websocket)

    try:
        await message_loop(websocket, parser, handler)
    except WebSocketDisconnect:
        await manager.disconnect(game_id, websocket)