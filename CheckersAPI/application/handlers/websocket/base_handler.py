from abc import ABC, abstractmethod

class WebSocketHandler(ABC):
    @abstractmethod
    async def handle(self, game_id: str, player_id: str, data: any):
        pass
