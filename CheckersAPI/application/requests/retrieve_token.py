from dataclasses import dataclass


@dataclass
class RetrieveToken:
    client_host: str
    accept_language: str
    username: str
    password: str