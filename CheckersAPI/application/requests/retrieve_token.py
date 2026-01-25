from dataclasses import dataclass


@dataclass
class RetrieveToken:
    client_host: str
    agent: str
    accept_language: str

    @property
    def is_guest(self) -> bool:
        return False


@dataclass
class RetrieveGuestToken(RetrieveToken):
    @property
    def is_guest(self) -> bool:
        return True


@dataclass
class RetrieveProfileToken(RetrieveToken):
    username: str
    password: str