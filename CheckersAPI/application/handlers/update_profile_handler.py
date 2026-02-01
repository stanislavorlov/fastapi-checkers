import logging
from application.handlers.base_handler import RequestHandler
from application.requests.update_profile import UpdateProfileRequest
from infrastructure.repositories.player_repository import PlayerRepository
from domain.player.display_name import DisplayName
from infrastructure.repositories.profile_repository import ProfileRepository

logger = logging.getLogger(__name__)

class UpdateProfileHandler(RequestHandler[UpdateProfileRequest, bool]):
    def __init__(self, profile_repository: ProfileRepository, player_repository: PlayerRepository):
        self.profile_repository = profile_repository
        self.player_repository = player_repository

    async def handle(self, request: UpdateProfileRequest) -> bool:
        profile = self.profile_repository.get(request.profile_id)
        if not profile:
            logger.warning(f"Profile {request.profile_id} not found for update")
            return False

        update_data = {
            k: v for k, v in vars(request).items() 
            if v is not None and k != 'profile_id'
        }
        
        profile.update_profile(**update_data)
        self.profile_repository.save(profile)

        # Sync Player display name
        player = self.player_repository.get_by_profile_id(request.profile_id)
        if player:
            new_display_name = str(profile.full_name) if profile.full_name else profile.contact.username
            player.update_player(
                display_name=DisplayName(display_name=new_display_name),
                type_=player.type_
            )
            self.player_repository.save(player)
            logger.info(f"Player {player.id} display name synced with profile")
        
        return True
