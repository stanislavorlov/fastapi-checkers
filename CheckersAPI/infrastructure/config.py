import os
from dotenv import load_dotenv

def getenv_int(name, default=0):
    value = os.getenv(name)
    try:
        return int(value)
    except (TypeError, ValueError):
        return default

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ISSUER = os.getenv("ISSUER")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = getenv_int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"), 30)
AUDIENCE =os.getenv("AUDIENCE")
DATABASE_URL=os.getenv('DATABASE_URL')
DATABASE_NAME=os.getenv('DATABASE_NAME')