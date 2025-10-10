from collections import defaultdict
from starlette.websockets import WebSocket


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
