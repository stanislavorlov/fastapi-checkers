import json
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from starlette.middleware.cors import CORSMiddleware
from starlette.websockets import WebSocket, WebSocketDisconnect
from web.dependencies import get_websocket_dispatcher
from application.handlers.websocket.dispatcher import WebSocketDispatcher
from web.routers import game_api, accounts_api, session_api, history_api
from infrastructure.runtime import connection_manager as manager
from web.exception_handlers import global_exception_handler
from infrastructure.mongo_context import MongoContext

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
        # Create TTL indexes on startup
        MongoContext().ensure_indexes()
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
app.include_router(history_api.router)

async def message_loop(
    game_id: str, 
    websocket: WebSocket, 
    dispatcher: WebSocketDispatcher,
    player_id: str = None
):
    while True:
        try:
            message = await websocket.receive_text()
            logger.debug(f"message received: {message}")
            
            data = json.loads(message)
            msg_type = data.get('type')
            msg_data = data.get('data')

            if msg_type:
                await dispatcher.dispatch(msg_type, game_id, player_id, msg_data)
                #if msg_type == 'abandon':
                #    break
            else:
                logger.warning(f"Received message without type: {message}")

        except json.JSONDecodeError:
            logger.error("Error decoding JSON message")
        except Exception as e:
            logger.error(f"Unexpected error in message loop: {e}")
            raise # Re-raise for websocket_endpoint cleanup

@app.websocket("/ws/{game_id}")
async def websocket_endpoint(
        websocket: WebSocket,
        game_id: str,
        player_id: str = None,
        dispatcher: WebSocketDispatcher = Depends(get_websocket_dispatcher)
):
    await manager.connect(game_id, websocket)

    try:
        await message_loop(game_id, websocket, dispatcher, player_id)
    except WebSocketDisconnect:
        await manager.disconnect(game_id, websocket)