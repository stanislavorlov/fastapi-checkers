from application.requests.retrieve_token import RetrieveToken
from domain.player.player import Player
from domain.player.player_type import PlayerType
from domain.profile.full_name import FullName
from infrastructure.repositories.session_token_repository import SessionRepository
from web.models import AccessToken
from web.token_helper import create_access_token


class GuestTokenHandler:

    def __init__(self,
                 session_repository: SessionRepository):
        self.session_repository = session_repository

    def handle(self, request: RetrieveToken) -> AccessToken:
        guest_player = Player.create(
            Player,
            PlayerType.GUEST,
            "intermediate",
            None
        )

        token = create_access_token(
            str(guest_player.id),
            f'Guest Player {guest_id}',
            f'guest_player_{guest_id}@email.com',
            'guest')

        session_token_repository.create_session(token)