import json
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from starlette.middleware.cors import CORSMiddleware
from starlette.websockets import WebSocket, WebSocketDisconnect
from application.handlers.game_event_handler import GameEventHandler
from infrastructure.event_parser import EventParser
from web.dependencies import get_event_parser, get_game_event_handler
from web.routers import game_api, accounts_api, session_api
from infrastructure.runtime import connection_manager as manager
from web.exception_handlers import global_exception_handler

# Configure root logging once
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

logger = logging.getLogger(__name__)

# "Log everything as DEBUG, EXCEPT noisy libraries"
logging.getLogger("pymongo").setLevel(logging.WARNING)
logging.getLogger("python_multipart").setLevel(logging.WARNING)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 App started")
    try:
        yield
    finally:
        logger.info("🛑 Shutting down. Closing all WebSocket connections...")
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


app.add_exception_handler(Exception, global_exception_handler)

app.include_router(game_api.router)
app.include_router(accounts_api.router)
app.include_router(session_api.router)

async def message_loop(game_id: str, websocket: WebSocket, parser: EventParser, handler: GameEventHandler):
    while True:
        move_message = await websocket.receive_text()
        logger.debug(f"message received: {move_message}")

        try:
            player, pdn_move = parser.parse(move_message)
            await handler.handle(game_id, player, pdn_move)

        except json.decoder.JSONDecodeError:
            logger.error("Error decoding JSON")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")

@app.websocket("/ws/{game_id}")
async def websocket_endpoint(
        websocket: WebSocket,
        game_id: str,
        parser: EventParser = Depends(get_event_parser),
        handler: GameEventHandler = Depends(get_game_event_handler)
):
    await manager.connect(game_id, websocket)

    try:
        await message_loop(game_id, websocket, parser, handler)
    except WebSocketDisconnect:
        await manager.disconnect(game_id, websocket)