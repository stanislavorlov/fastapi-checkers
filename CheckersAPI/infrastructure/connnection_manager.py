import logging
from collections import defaultdict
from starlette.websockets import WebSocket


logger = logging.getLogger(__name__)

class ConnectionManager:
    def __init__(self):
        import uuid
        self.id = uuid.uuid4()
        self.active_connections: dict[str, list[WebSocket]] = defaultdict(list)
        self.match_connections: dict[str, WebSocket] = {}
        logger.info(f"ConnectionManager initialized with ID: {self.id}")

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

    async def connect_matchmaking(self, player_id: str, websocket: WebSocket):
        logger.info(f"Adding matchmaking connection for player: {player_id}")
        await websocket.accept()
        self.match_connections[player_id] = websocket
        logger.debug(f"Current match_connections: {list(self.match_connections.keys())}")

    async def disconnect_matchmaking(self, player_id: str):
        logger.info(f"Removing matchmaking connection for player: {player_id}")
        self.match_connections.pop(player_id, None)
        logger.debug(f"Current match_connections: {list(self.match_connections.keys())}")

    async def send_to_player(self, player_id: str, message: str):
        logger.debug(f"[Manager {self.id}] Attempting to send message to player {player_id}. Active match connections: {list(self.match_connections.keys())}")
        if player_id in self.match_connections:
            try:
                websocket = self.match_connections[player_id]
                logger.debug(f"[Manager {self.id}] Sending message to player {player_id}, connection: {websocket}")
                await websocket.send_text(message)
                logger.info(f"[Manager {self.id}] Successfully sent match notification to {player_id}")
            except Exception as e:
                logger.error(f"[Manager {self.id}] Error sending message to player {player_id}: {e}")
                self.match_connections.pop(player_id, None)
        else:
            logger.warning(f"[Manager {self.id}] No active matchmaking connection found for player {player_id}")

    async def close_all(self):
        logger.debug('Closing all active socket connections: %s', self.active_connections)
        for game_id in self.active_connections:
            for ws in self.active_connections[game_id]:
                await ws.close()
            self.active_connections[game_id].clear()
        
        for player_id in list(self.match_connections.keys()):
            try:
                await self.match_connections[player_id].close()
            except:
                pass
        self.match_connections.clear()
