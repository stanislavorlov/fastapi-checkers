import secrets
import string
from datetime import timedelta, datetime, timezone
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt import InvalidTokenError
from pwdlib import PasswordHash
from infrastructure.config import ACCESS_TOKEN_EXPIRE_MINUTES, ISSUER, AUDIENCE, SECRET_KEY, ALGORITHM
from infrastructure.repositories.user_repository import UserRepository
from infrastructure.schemas import guest_user
from web.models import AccessTokenData

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

def create_access_token(data: AccessTokenData, expires_delta: timedelta | None = None):
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

    to_encode = data.model_dump()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    to_encode.update({"iss": ISSUER})
    to_encode.update({"aud": AUDIENCE})
    #to_encode.update({"type": token_type})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt

def decode_access_token(token: str) -> AccessTokenData:
    payload = jwt.decode(
        jwt=token,
        key=SECRET_KEY,
        audience=AUDIENCE,
        issuer=ISSUER,
        algorithms=[ALGORITHM])

    return AccessTokenData(
        sub=payload["sub"],
        type=payload['type'],
        preferred_username=payload['preferred_username'],
        name=payload['name'],
    )

async def get_current_user(token: str = Depends(oauth2_scheme)):
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

        return UserRepository().get_user_profile(user_id)

    except InvalidTokenError:
        print('Invalid token')

        raise credentials_exception