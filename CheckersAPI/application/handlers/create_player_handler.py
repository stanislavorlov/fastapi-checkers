import logging
from typing import Optional
from application.requests.create_player import CreatePlayerRequest
from domain.player.player import Player
from domain.profile.profile import Profile
from infrastructure.repositories.player_repository import PlayerRepository
from infrastructure.repositories.profile_repository import ProfileRepository
from application.handlers.base_handler import RequestHandler
from domain.player.player_identity import PlayerIdentity


logger = logging.getLogger(__name__)

class CreatePlayerHandler(RequestHandler[CreatePlayerRequest, str]):

    def __init__(self,
            profile_repository: ProfileRepository,
            player_repository: PlayerRepository):

        self.profile_repository = profile_repository
        self.player_repository = player_repository

    async def handle(self, request: CreatePlayerRequest) -> str:
        """
        Method handles the creation of a new player when a new guest joins or accounts log in
        """
        profile: Optional[Profile] = None

        if request.profile_id:
            profile = self.profile_repository.get(request.profile_id)

        identity = PlayerIdentity(type_=request.type, profile_id=request.profile_id)

        player = Player.create(
            identity,
            request.player_level,
            profile)

        logger.debug(f"Created new player {player}")

        return self.player_repository.create(player)