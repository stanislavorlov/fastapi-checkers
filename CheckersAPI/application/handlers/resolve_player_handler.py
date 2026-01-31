import logging
from fastapi import Request, HTTPException
from application.handlers.create_player_handler import CreatePlayerHandler
from application.handlers.resolve_guest_player_handler import ResolveGuestPlayerHandler
from web.token_helper import decode_access_token

logger = logging.getLogger(__name__)

class ResolvePlayerHandler:
    def __init__(
        self,
        player_handler: CreatePlayerHandler,
        resolve_guest_player_handler: ResolveGuestPlayerHandler
    ):
        self.player_handler = player_handler
        self.resolve_guest_player_handler = resolve_guest_player_handler

    async def handle(self, request: Request) -> str:
        auth_header = request.headers.get("Authorization")
        if auth_header:
            try:
                token = auth_header.split(" ")[1]
                payload = decode_access_token(token)
                return payload.sub
            except Exception:
                raise HTTPException(status_code=401, detail="Invalid authentication credentials")
        
        # Resolve guest player idempotently
        client_host = request.client.host if request.client else "unknown"
        agent = request.headers.get("User-Agent", "unknown")
        
        return self.resolve_guest_player_handler.handle(client_host, agent)
