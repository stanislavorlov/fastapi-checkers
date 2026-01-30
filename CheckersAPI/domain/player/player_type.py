from enum import Enum


class PlayerType(str, Enum):
    GUEST = "guest"
    ACCOUNT = "account"
    AI = "bot"