from application.requests.retrieve_token import RetrieveToken
from infrastructure.repositories.profile_repository import ProfileRepository
from web.token_helper import create_access_token, verify_password


class RetrieveTokenHandler:

    def __init__(self, profile_repository: ProfileRepository):
        self.profile_repository = profile_repository

    def handle(self, request: RetrieveToken) -> str:
        profile = self.profile_repository.find_by_email(request.username)

        if profile is None:
            print('Profile not found')
            return None

        hashed_password = profile.password_hash

        if not verify_password(request.password, hashed_password):
            print('Invalid password')
            return None

        # ToDo: store token in database
        access_token = create_access_token(
            str(profile.id),
            f"{profile.first_name} {profile.last_name}",
            profile.email,
            'user')

        return access_token