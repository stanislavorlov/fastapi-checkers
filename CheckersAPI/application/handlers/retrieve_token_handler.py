from application.requests.retrieve_token import RetrieveToken
from infrastructure.repositories.player_repository import PlayerRepository
from infrastructure.repositories.profile_repository import ProfileRepository
from infrastructure.repositories.session_token_repository import SessionRepository
from web.models import AccessToken
from web.token_helper import create_access_token, verify_password


class RetrieveTokenHandler:

    def __init__(self,
                 profile_repository: ProfileRepository,
                 session_repository: SessionRepository,
                 player_repository: PlayerRepository):

        self.profile_repository = profile_repository
        self.session_repository = session_repository
        self.player_repository = player_repository

    def handle(self, request: RetrieveToken) -> AccessToken:
        profile = self.profile_repository.find_by_email(request.username)

        if profile is None:
            print('Profile not found')
            return None

        player = self.player_repository.get_by_profile_id(profile.id)

        hashed_password = profile.password_hash

        if not verify_password(request.password, hashed_password):
            print('Invalid password')
            return None

        access_token = create_access_token(
            str(player.id),
            str(profile.full_name),
            profile.contact.email,
            'user')

        self.session_repository.create_session(
            player.id,
            access_token.access_token,
            request.client_host,
            agent=request.agent,
            region='',
            timezone=''
        )

        return access_token