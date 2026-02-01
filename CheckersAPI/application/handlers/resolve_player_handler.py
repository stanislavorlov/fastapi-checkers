import logging
from fastapi import HTTPException
from application.handlers.create_player_handler import CreatePlayerHandler
from application.handlers.resolve_guest_player_handler import ResolveGuestPlayerHandler
from web.token_helper import decode_access_token
from application.handlers.base_handler import RequestHandler
from application.requests.resolve_player import ResolvePlayerRequest

logger = logging.getLogger(__name__)

class ResolvePlayerHandler(RequestHandler[ResolvePlayerRequest, str]):
    def __init__(
        self,
        player_handler: CreatePlayerHandler,
        resolve_guest_player_handler: ResolveGuestPlayerHandler
    ):
        self.player_handler = player_handler
        self.resolve_guest_player_handler = resolve_guest_player_handler

    async def handle(self, request: ResolvePlayerRequest) -> str:
        auth_header = request.auth_header
        if auth_header:
            try:
                token = auth_header.split(" ")[1]
                payload = decode_access_token(token)
                return payload.sub
            except Exception:
                raise HTTPException(status_code=401, detail="Invalid authentication credentials")
        
        # Resolve guest player idempotently
        client_host = request.client_host
        agent = request.user_agent
        
        from application.requests.resolve_guest_player import ResolveGuestPlayerRequest
        return await self.resolve_guest_player_handler.handle(ResolveGuestPlayerRequest(host=client_host, agent=agent))
