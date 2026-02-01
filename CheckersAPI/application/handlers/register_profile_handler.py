from domain.profile.contact import Contact
from domain.profile.full_name import FullName
from domain.profile.profile import Profile
from infrastructure.repositories.profile_repository import ProfileRepository
from web.token_helper import hash_password
from application.handlers.base_handler import RequestHandler
from application.requests.register_profile import RegisterProfileRequest


class RegisterProfileHandler(RequestHandler[RegisterProfileRequest, str]):

    def __init__(self, profile_repository: ProfileRepository):
        self.profile_repository = profile_repository

    async def handle(self, request: RegisterProfileRequest) -> str:

        username = request.email.split('@')[0]

        profile = Profile(
            password_hash=hash_password(request.password),
            contact=Contact(
                contact=f"{username} <{request.email}>"
            ),
            initial_level=request.level,
            full_name=FullName.create(first=request.first_name, last=request.last_name),
            language=request.language,
            country=request.country,
        )

        return self.profile_repository.create(profile)
