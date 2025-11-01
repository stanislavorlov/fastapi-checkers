from domain.profile.full_name import FirstName, LastName
from domain.profile.profile import Profile
from infrastructure.repositories.profile_repository import ProfileRepository
from web.models import CreateAccountDto
from web.token_helper import hash_password


class RegisterProfileHandler:

    def __init__(self, profile_repository: ProfileRepository):
        self.profile_repository = profile_repository

    def handle(self,
               request: CreateAccountDto):

        profile = Profile(
            email=request.email,
            password_hash=hash_password(request.password),
            username=request.username,
            first_name=FirstName(request.first_name),
            last_name=LastName(request.last_name),
            country=request.country,
            language= request.language,
        )

        self.profile_repository.create(profile)

        # ToDo: create ranks and stats during player creation - on game startup

