import logging
from application.handlers.create_player_handler import CreatePlayerHandler
from application.requests.create_player import CreatePlayerRequest
from application.requests.retrieve_token import RetrieveToken, RetrieveProfileToken
from domain.player.player_type import PlayerType
from infrastructure.repositories.player_repository import PlayerRepository
from infrastructure.repositories.profile_repository import ProfileRepository
from infrastructure.repositories.session_token_repository import SessionRepository
from web.models import AccessToken
from web.token_helper import create_access_token, verify_password

logger = logging.getLogger(__name__)

class RetrieveTokenHandler:

    def __init__(self,
                 profile_repository: ProfileRepository,
                 session_repository: SessionRepository,
                 player_repository: PlayerRepository,
                 create_player_handler: CreatePlayerHandler):

        self.profile_repository = profile_repository
        self.session_repository = session_repository
        self.player_repository = player_repository
        self.create_player_handler = create_player_handler

    def handle(self, request: RetrieveToken) -> AccessToken:
        # Guest Flow
        if request.is_guest:
            logger.info('Processing Guest Token request')
            
            # Check if this guest already has a recent session
            existing_player_id = self.session_repository.find_recent_guest_session(
                request.client_host, 
                request.agent
            )
            
            if existing_player_id:
                logger.info('Found recent guest session for player %s, reusing', existing_player_id)
                player_id = existing_player_id
            else:
                create_player_request = CreatePlayerRequest(
                    type=PlayerType.GUEST,
                    player_level=''
                )
                player_id = self.create_player_handler.handle(create_player_request)
                logger.info('Created new Guest Player %s', player_id)

            access_token = create_access_token(
                player_id,
                'Guest',
                f'guest_{player_id}@checkers.local',
                'guest'
            )
        else:
            # Account Flow
            profile_request: RetrieveProfileToken = request # for type hinting
            logger.info(f'Processing Account Token request for: {profile_request.username}')
            profile = self.profile_repository.find_by_email(profile_request.username)

            if profile is None:
                logger.warning(f'Profile not found for username: {profile_request.username}')
                return None

            hashed_password = profile.password_hash

            if not verify_password(profile_request.password, hashed_password):
                logger.warning(f'Invalid password for username: {profile_request.username}')
                return None

            player = self.player_repository.get_by_profile_id(profile.id)
            
            if player is None:
                # Fallback if player doesn't exist for profile (e.g. migration or partial registration)
                logger.info(f'Player not found for profile {profile.id}, creating one')
                create_player_request = CreatePlayerRequest(
                    type=PlayerType.ACCOUNT,
                    profile_id=profile.id,
                    player_level=profile.initial_level
                )
                player_id = self.create_player_handler.handle(create_player_request)
            else:
                player_id = str(player.id)

            access_token = create_access_token(
                player_id,
                str(profile.full_name),
                profile.contact.email,
                'user'
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