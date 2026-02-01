import logging
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
from infrastructure.repositories.player_repository import PlayerRepository
from web.models import AccessTokenData, AccessToken, PlayerUserDto

password_hash = PasswordHash.recommended()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/token")
logger = logging.getLogger(__name__)

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

def create_access_token(player_id: str, name: str, email: str, access_type: str) -> AccessToken:
    access_token_data = AccessTokenData(
        sub=player_id,
        name=name,
        preferred_username=email,
        type=access_type,
        exp=datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        iss=settings.ISSUER,
        aud=settings.AUDIENCE,
    )

    access_token = jwt.encode(access_token_data.model_dump(), settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    refresh_token_data = AccessTokenData(
        sub=player_id,
        name=name,
        preferred_username=email,
        type=access_type,
        exp=datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
        iss=settings.ISSUER,
        aud=settings.AUDIENCE,
    )

    refresh_token = jwt.encode(refresh_token_data.model_dump(), settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    return AccessToken(
        player_id=player_id,
        access_token=access_token,
        refresh_token=refresh_token,
        name=name,
        email=email,
        type=access_type
    )

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

async def get_current_user(
        profile_repository: ProfileRepository,
        player_repository: PlayerRepository,
        token: str
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_access_token(token)
        player_id, user_type = payload.sub, payload.type

        if player_id is None:
            logger.error('Player ID (sub) is None in JWT payload')
            raise credentials_exception

        player = player_repository.get_by_id(player_id)
        if player is None:
            logger.error(f'Player {player_id} not found')
            raise credentials_exception
        
        if user_type == "guest":
            return PlayerUserDto(
                player_id=str(player.id),
                email='',
                first_name='Guest',
                last_name='Guest',
                country='',
                anonymous=True
            )

        if player.profile_id:
            profile = profile_repository.get(str(player.profile_id))
            if profile:
                first_name = profile.full_name.first.value if profile.full_name else profile.contact.username
                last_name = profile.full_name.last.value if profile.full_name else ''
                
                return PlayerUserDto(
                    player_id=str(player.id),
                    email=profile.contact.email,
                    first_name=first_name,
                    last_name=last_name,
                    country=profile.country or '',
                    anonymous=False
                )

        return PlayerUserDto(
            player_id=str(player.id),
            email='',
            first_name=player.display_name.value,
            last_name='',
            country='',
            anonymous=False
        )

    except InvalidTokenError as e:
        if "expired" in str(e).lower():
            logger.info(f'Token expired: {e}')
        else:
            logger.error(f'Invalid token: {e}')
            
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Could not validate credentials: {e}",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        logger.error(f'Unexpected error in get_current_user: {e}')
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {e}",
        )