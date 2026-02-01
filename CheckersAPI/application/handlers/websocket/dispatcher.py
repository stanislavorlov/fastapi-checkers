import logging
from typing import Dict
from application.handlers.websocket.base_handler import WebSocketHandler

logger = logging.getLogger(__name__)

class WebSocketDispatcher:
    def __init__(self):
        self._handlers: Dict[str, WebSocketHandler] = {}

    def register_handler(self, message_type: str, handler: WebSocketHandler):
        self._handlers[message_type] = handler
        logger.debug(f"Registered WebSocket handler for type: {message_type}")

    async def dispatch(self, message_type: str, game_id: str, player_id: str, data: any):
        handler = self._handlers.get(message_type)
        if handler:
            await handler.handle(game_id, player_id, data)
        else:
            logger.warning(f"No WebSocket handler found for message type: {message_type}")
