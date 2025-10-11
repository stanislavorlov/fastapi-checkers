import secrets
import string
from datetime import timedelta, datetime, timezone
from typing import Annotated
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt import InvalidTokenError
from pwdlib import PasswordHash
from infrastructure.config import ACCESS_TOKEN_EXPIRE_MINUTES, ISSUER, AUDIENCE, SECRET_KEY, ALGORITHM
from infrastructure.database import user_collection
from infrastructure.schemas import single_player
from web.models import AccessTokenData, RequestComputerGameDto

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

def create_access_token(data: AccessTokenData, token_type: str = "user", expires_delta: timedelta | None = None):
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
    to_encode.update({"type": token_type})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            jwt=token,
            key=SECRET_KEY,
            audience=AUDIENCE,
            issuer=ISSUER,
            algorithms=[ALGORITHM])

        user_id = payload.get("sub")
        user_type = payload.get("type", "user")

        if user_type == "guest":
            guest_random_id = nanoid(10)

            return {
                "player_id": guest_random_id,
                "email": '',
                "first_name": f"Guest{guest_random_id}",
                "last_name": '',
                "country": '',
            }

        if user_id is None:
            raise credentials_exception

    except InvalidTokenError:
        raise credentials_exception

    if user_type == "user":
        player_dict = user_collection.find_one({"user_id": user_id})
        if player_dict is None:
            raise credentials_exception

        return single_player(player_dict)

    return None # to do Guest