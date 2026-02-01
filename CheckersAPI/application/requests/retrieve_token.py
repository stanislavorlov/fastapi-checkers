from dataclasses import dataclass
from typing import Optional


@dataclass(kw_only=True)
class RetrieveToken:
    client_host: str
    agent: str
    accept_language: str
    region: Optional[str] = None
    timezone: Optional[str] = None

    @property
    def is_guest(self) -> bool:
        return False


@dataclass(kw_only=True)
class RetrieveGuestToken(RetrieveToken):
    @property
    def is_guest(self) -> bool:
        return True


@dataclass(kw_only=True)
class RetrieveProfileToken(RetrieveToken):
    username: str
    password: str