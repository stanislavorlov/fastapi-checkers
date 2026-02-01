import logging
from application.mediator import Mediator
from application.requests.move import MoveRequest
from application.requests.abandon_game import AbandonGameRequest

logger = logging.getLogger(__name__)

class WebSocketDispatcher:
    def __init__(self, mediator: Mediator):
        self.mediator = mediator

    async def dispatch(self, message_type: str, game_id: str, player_id: str, data: any):
        request = None
        if message_type == 'move':
            request = MoveRequest(game_id=game_id, player_id=player_id, data=data)
        elif message_type == 'abandon':
            request = AbandonGameRequest(game_id=game_id, player_id=player_id)
        
        if request:
            await self.mediator.send(request)
        else:
            logger.warning(f"No request mapping found for message type: {message_type}")
