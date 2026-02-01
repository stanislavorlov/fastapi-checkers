import logging
import threading
from application.handlers.create_player_handler import CreatePlayerHandler
from application.requests.create_player import CreatePlayerRequest
from domain.player.player_type import PlayerType
from infrastructure.repositories.session_token_repository import SessionRepository
from application.handlers.base_handler import RequestHandler
from application.requests.resolve_guest_player import ResolveGuestPlayerRequest

logger = logging.getLogger(__name__)

class ResolveGuestPlayerHandler(RequestHandler[ResolveGuestPlayerRequest, str]):
    _lock = threading.Lock()

    def __init__(self, 
                 session_repository: SessionRepository,
                 create_player_handler: CreatePlayerHandler):
        self.session_repository = session_repository
        self.create_player_handler = create_player_handler

    async def handle(self, request: ResolveGuestPlayerRequest) -> str:
        """
        Resolves a guest player ID by either reusing a recent session or creating a new player.
        Atomic operation to prevent race conditions during concurrent requests.
        """
        host = request.host
        agent = request.agent

        logger.info('Resolving guest player for host=%s, agent=%s', host, agent)
        
        with self._lock:
            player_id = self.session_repository.find_recent_guest_session(host, agent)
            
            if player_id:
                logger.info('Found recent guest session for player %s, reusing', player_id)
                return player_id

            create_player_request = CreatePlayerRequest(
                type=PlayerType.GUEST,
                player_level='1'
            )
            player_id = await self.create_player_handler.handle(create_player_request)
            logger.info('Created new Guest Player %s', player_id)

            return player_id
