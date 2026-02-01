import logging
from collections import namedtuple
from typing import Optional
from application.handlers.create_player_handler import CreatePlayerHandler
from application.handlers.resolve_guest_player_handler import ResolveGuestPlayerHandler
from application.requests.create_player import CreatePlayerRequest
from application.requests.retrieve_token import RetrieveToken, RetrieveProfileToken
from domain.player.player_type import PlayerType
from infrastructure.repositories.player_repository import PlayerRepository
from infrastructure.repositories.profile_repository import ProfileRepository
from web.models import AccessToken
from web.token_helper import create_access_token, verify_password, decode_access_token, InvalidTokenError
from application.handlers.base_handler import RequestHandler

logger = logging.getLogger(__name__)
AuthResult = namedtuple('AuthResult', ['player_id', 'display_name', 'email', 'type'])

class RetrieveTokenHandler(RequestHandler[RetrieveToken, AccessToken]):

    def __init__(self,
                 profile_repository: ProfileRepository,
                 player_repository: PlayerRepository,
                 create_player_handler: CreatePlayerHandler,
                 resolve_guest_player_handler: ResolveGuestPlayerHandler):

        self.profile_repository = profile_repository
        self.player_repository = player_repository
        self.create_player_handler = create_player_handler
        self.resolve_guest_player_handler = resolve_guest_player_handler

    async def handle(self, request: RetrieveToken) -> Optional[AccessToken]:
        if request.is_guest:
            auth_result = await self._handle_guest_auth(request)
        else:
            auth_result = await self._handle_account_auth(request)

        if auth_result is None:
            return None

        # Check if we already have an active session for this player/client
        existing_token = self.player_repository.find_session_by_player_and_client(
            auth_result.player_id, 
            request.client_host, 
            request.agent
        )
        
        if existing_token:
            try:
                # Validate the existing token before reusing it
                decode_access_token(existing_token)
                logger.info('Reusing valid existing session token for player %s', auth_result.player_id)
                
                return AccessToken(
                    access_token=existing_token,
                    token_type='bearer',
                    player_id=auth_result.player_id,
                    name=auth_result.display_name,
                    email=auth_result.email,
                    type=auth_result.type,
                    refresh_token='' 
                )
            except InvalidTokenError:
                logger.info('Existing session token for player %s is expired or invalid, creating new one', auth_result.player_id)
                pass

        access_token = create_access_token(
            auth_result.player_id,
            auth_result.display_name,
            auth_result.email,
            auth_result.type
        )

        # Add session to player aggregate
        player = self.player_repository.get_by_id(auth_result.player_id)
        if player:
            from domain.sessions.region import Region
            from datetime import timezone
            try:
                from zoneinfo import ZoneInfo
            except ImportError:
                # Fallback for environments without zoneinfo (though Python 3.9+ should have it)
                ZoneInfo = None

            # Use request context if available
            session_region = Region(code=request.region) if request.region else None
            
            session_tz = timezone.utc
            if request.timezone and ZoneInfo:
                try:
                    session_tz = ZoneInfo(request.timezone)
                except Exception:
                    logger.warning(f"Invalid timezone received: {request.timezone}, falling back to UTC")
            
            player.create_session(
                session_token=access_token.access_token,
                host=request.client_host,
                agent=request.agent,
                region=session_region,
                tz=session_tz
            )
            self.player_repository.save(player)
            logger.info('Created new session for player %s', auth_result.player_id)

        return access_token

    async def _handle_guest_auth(self, request: RetrieveToken) -> AuthResult:
        logger.info('Processing Guest Token request')
        
        from application.requests.resolve_guest_player import ResolveGuestPlayerRequest
        player_id = await self.resolve_guest_player_handler.handle(
            ResolveGuestPlayerRequest(host=request.client_host, agent=request.agent)
        )
        
        return AuthResult(
            player_id=player_id,
            display_name='Guest',
            email=f'guest_{player_id}@checkers.local',
            type='guest'
        )

    async def _handle_account_auth(self, request: RetrieveProfileToken) -> Optional[AuthResult]:
        logger.info(f'Processing Account Token request for: {request.username}')
        profile = self.profile_repository.find_by_email(request.username)

        if profile is None:
            logger.warning(f'Profile not found for username: {request.username}')
            return None

        if not verify_password(request.password, profile.password_hash):
            logger.warning(f'Invalid password for username: {request.username}')
            return None

        player = self.player_repository.get_by_profile_id(profile.id)
        
        if player is None:
            logger.info(f'Player not found for profile {profile.id}, creating one')
            create_player_request = CreatePlayerRequest(
                type=PlayerType.ACCOUNT,
                profile_id=profile.id,
                player_level=profile.initial_level
            )
            player_id = await self.create_player_handler.handle(create_player_request)
        else:
            player_id = str(player.id)

        return AuthResult(
            player_id=player_id,
            display_name=str(profile.full_name),
            email=profile.contact.email,
            type='user'
        )