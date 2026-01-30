import logging
from collections import defaultdict
from starlette.websockets import WebSocket


logger = logging.getLogger(__name__)

class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, list[WebSocket]] = defaultdict(list)

    async def connect(self, game_id: str, websocket: WebSocket):
        game_id = str(game_id)
        await websocket.accept()
        self.active_connections[game_id].append(websocket)

    async def disconnect(self, game_id: str, websocket: WebSocket):
        game_id = str(game_id)
        logger.debug(f'disconnecting: %s, %s', game_id, websocket)
        if game_id in self.active_connections:
            if websocket in self.active_connections[game_id]:
                self.active_connections[game_id].remove(websocket)

    async def broadcast(self, game_id: str, message: str):
        game_id = str(game_id)
        logger.debug(f"Broadcasting messages into game: {game_id}")
        
        if game_id in self.active_connections:
            # Create a copy of the list to avoid issues if a socket disconnects during iteration
            for websocket in list(self.active_connections[game_id]):
                try:
                    logger.debug(f"Broadcasting to active Web Socket connection in game {game_id}")
                    await websocket.send_text(message)
                except Exception as e:
                    logger.error(f"Error broadcasting to websocket in game {game_id}: {e}")
                    # Optionally handle stale connections here
                    try:
                        self.active_connections[game_id].remove(websocket)
                    except ValueError:
                        pass

    async def close_all(self):
        logger.debug('Closing all active socket connections: %s', self.active_connections)
        for idx, game_id in enumerate(self.active_connections):
            for ws in self.active_connections[game_id]:
                await ws.close()
            self.active_connections[game_id].clear()
