import json
import logging
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from starlette.middleware.cors import CORSMiddleware
from starlette.websockets import WebSocket, WebSocketDisconnect
from web.routers import game_api, accounts_api, session_api, history_api
from infrastructure.runtime import connection_manager as manager
from web.dependencies import get_websocket_dispatcher, mongo_context
from application.handlers.websocket.dispatcher import WebSocketDispatcher
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
    
    async def matchmaking_task():
        from infrastructure.repositories.matching_repository import MatchingRepository
        from infrastructure.repositories.game_repository import GameRepository
        from infrastructure.repositories.player_repository import PlayerRepository
        from application.matchmaking_manager import MatchmakingManager
        
        match_repo = MatchingRepository(mongo_context)
        player_repo = PlayerRepository(mongo_context)
        game_repo = GameRepository(mongo_context, player_repo)
        
        mm_manager = MatchmakingManager(match_repo, game_repo, player_repo, manager)
        
        while True:
            try:
                await mm_manager.run_tick()
            except Exception as e:
                logger.error(f"Error in matchmaking loop: {e}")
            await asyncio.sleep(5)  # Tick every 5 seconds

    background_task = asyncio.create_task(matchmaking_task())

    try:
        # Create TTL indexes on startup
        mongo_context.ensure_indexes()
        yield
    finally:
        logger.info("🛑 Shutting down. Closing all WebSocket connections...")
        background_task.cancel()
        await manager.close_all()

app = FastAPI(lifespan=lifespan)

origins = [
    'http://localhost:4200',
    'http://0.0.0.0:4200',
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'], # Allow all origins for local network testing
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

@app.websocket("/ws/matchmaking/{player_id}")
async def matchmaking_websocket_endpoint(
        websocket: WebSocket,
        player_id: str
):
    logger.info(f"Matchmaking WebSocket connection attempt for player_id: {player_id} using manager {manager.id}")
    await manager.connect_matchmaking(player_id, websocket)
    try:
        while True:
            # Keep connection alive, we only send messages from server
            data = await websocket.receive_text()
            logger.debug(f"Received heartbeat/data from matchmaking client {player_id}: {data}")
    except WebSocketDisconnect:
        logger.info(f"Matchmaking WebSocket disconnected for player_id: {player_id}")
        await manager.disconnect_matchmaking(player_id)
    except Exception as e:
        logger.error(f"Error in matchmaking WebSocket for {player_id}: {e}")
        await manager.disconnect_matchmaking(player_id)