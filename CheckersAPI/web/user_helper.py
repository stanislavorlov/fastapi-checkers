import secrets
import string
from datetime import timedelta, datetime, timezone
import jwt
from pwdlib import PasswordHash
from web.models import AccessTokenData

password_hash = PasswordHash.recommended()

# ToDo: move SECRET to .env file
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
ISSUER = "https://checkers.com"
AUDIENCE = "checkers-app-frontend"

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

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt