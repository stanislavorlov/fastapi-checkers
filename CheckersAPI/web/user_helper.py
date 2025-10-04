import hashlib
import secrets
import string
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def nanoid(size: int = 21) -> str:
    """
    Method generates TypeScript alternative of nanoid()
    """
    alphabet = string.ascii_letters + string.digits + "_-"
    return ''.join(secrets.choice(alphabet) for _ in range(size))

def hash_password(password: str) -> str:
    sha256 = hashlib.sha256(password.encode()).digest()  # raw bytes
    return pwd_context.hash(sha256)

def verify_password(password: str, hashed: str) -> bool:
    sha256 = hashlib.sha256(password.encode()).digest()
    return pwd_context.verify(sha256, hashed)