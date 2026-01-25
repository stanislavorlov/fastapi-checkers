import logging
from collections import namedtuple
from application.handlers.create_player_handler import CreatePlayerHandler
from application.handlers.resolve_guest_player_handler import ResolveGuestPlayerHandler
from application.requests.create_player import CreatePlayerRequest
from application.requests.retrieve_token import RetrieveToken, RetrieveProfileToken
from domain.player.player_type import PlayerType
from infrastructure.repositories.player_repository import PlayerRepository
from infrastructure.repositories.profile_repository import ProfileRepository
from infrastructure.repositories.session_token_repository import SessionRepository
from web.models import AccessToken
from web.token_helper import create_access_token, verify_password

logger = logging.getLogger(__name__)

AuthResult = namedtuple('AuthResult', ['player_id', 'display_name', 'email', 'type'])

class RetrieveTokenHandler:

    def __init__(self,
                 profile_repository: ProfileRepository,
                 session_repository: SessionRepository,
                 player_repository: PlayerRepository,
                 create_player_handler: CreatePlayerHandler,
                 resolve_guest_player_handler: ResolveGuestPlayerHandler):

        self.profile_repository = profile_repository
        self.session_repository = session_repository
        self.player_repository = player_repository
        self.create_player_handler = create_player_handler
        self.resolve_guest_player_handler = resolve_guest_player_handler

    def handle(self, request: RetrieveToken) -> AccessToken:
        if request.is_guest:
            auth_result = self._handle_guest_auth(request)
        else:
            auth_result = self._handle_account_auth(request)

        if auth_result is None:
            return None

        # Check if we already have an active session for this player/client
        existing_token = self.session_repository.find_session_by_player_and_client(
            auth_result.player_id, 
            request.client_host, 
            request.agent
        )
        
        if existing_token:
            logger.info('Reusing existing session token for player %s', auth_result.player_id)
            # We return a partial AccessToken or just enough to satisfy the contract
            # Since the client needs the access_token, we can return it if it's still valid
            # For simplicity, we create a DTO with the existing token
            return AccessToken(
                access_token=existing_token,
                token_type='bearer',
                player_id=auth_result.player_id,
                name=auth_result.display_name,
                email=auth_result.email,
                type=auth_result.type,
                refresh_token='' # Refresh token logic might need more care if we want to reuse it too
            )

        access_token = create_access_token(
            auth_result.player_id,
            auth_result.display_name,
            auth_result.email,
            auth_result.type
        )

        self.session_repository.create_session(
            str(access_token.player_id),
            access_token.access_token,
            request.client_host,
            agent=request.agent,
            region='',
            timezone=''
        )

        return access_token

    def _handle_guest_auth(self, request: RetrieveToken) -> AuthResult:
        logger.info('Processing Guest Token request')
        
        player_id = self.resolve_guest_player_handler.handle(
            request.client_host, 
            request.agent
        )
        
        return AuthResult(
            player_id=player_id,
            display_name='Guest',
            email=f'guest_{player_id}@checkers.local',
            type='guest'
        )

    def _handle_account_auth(self, request: RetrieveProfileToken) -> AuthResult | None:
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
            player_id = self.create_player_handler.handle(create_player_request)
        else:
            player_id = str(player.id)

        return AuthResult(
            player_id=player_id,
            display_name=str(profile.full_name),
            email=profile.contact.email,
            type='user'
        )