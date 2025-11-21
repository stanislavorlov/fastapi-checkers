import secrets
import string
from datetime import timedelta, datetime, timezone
import jwt
from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt import InvalidTokenError
from pwdlib import PasswordHash
from infrastructure.settings import settings
from infrastructure.repositories.profile_repository import ProfileRepository
from infrastructure.mappers import guest_user
from web.models import AccessTokenData, AccessToken

password_hash = PasswordHash.recommended()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/token")

def nanoid(size: int = 21) -> str:
    """
    Method generates TypeScript alternative of nanoid()
    """
    alphabet = string.ascii_letters + string.digits + "_-"
    return ''.join(secrets.choice(alphabet) for _ in range(size))

def hash_password(password: str) -> str:
    return password_hash.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_hash.verify(plain_password, hashed_password)

def create_access_token(player_id: str, name: str, email: str, access_type: str):
    """
    Method creates an access token
    iss - Issuer claim containing StringOrURI value
    sub - Subject claim identifies the principal, should be globally unique value in the context of issuer
    aud - Recipients that the JWT is intended for. If the principal doesn't identify itself with a value in "aud",
    the token is rejected. StringOrURI value
    exp - expiration date time (few minutes). Must be a number
    nbf - current date time should be less than nbf value (not before)
    iat - the time JWT was issued at. Number containing a NumericDate
    jti - unique identifier for the JWT.
    """

    data = AccessTokenData(
        sub=player_id,
        name=name,
        preferred_username=email,
        type=access_type,
        exp=datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        iss=settings.ISSUER,
        aud=settings.AUDIENCE,
    )

    encoded_jwt = jwt.encode(data.model_dump(), settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    return AccessToken(player_id=player_id, access_token=encoded_jwt)

def decode_access_token(token: str) -> AccessTokenData:
    payload = jwt.decode(
        jwt=token,
        key=settings.SECRET_KEY,
        audience=settings.AUDIENCE,
        issuer=settings.ISSUER,
        algorithms=[settings.ALGORITHM])

    return AccessTokenData(
        sub=payload["sub"],
        type=payload['type'],
        preferred_username=payload['preferred_username'],
        name=payload['name'],
        exp=payload['exp'],
        iss=payload['iss'],
        aud=payload['aud'],
    )

# profile_repository: Annotated[ProfileRepository, Depends(get_profile_repository)],
# token: str = Depends(oauth2_scheme)
async def get_current_user(
        profile_repository: ProfileRepository,
        token: str
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_access_token(token)
        user_id, user_type = payload.sub, payload.type

        if user_type == "guest":
            guest_random_id = nanoid(10)

            return guest_user(guest_random_id)

        if user_id is None:
            print('User ID is None')

            raise credentials_exception

        return profile_repository.get(user_id)

    except InvalidTokenError:
        print('Invalid token')

        raise credentials_exception