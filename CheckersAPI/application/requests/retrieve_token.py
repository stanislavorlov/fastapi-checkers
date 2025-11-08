from dataclasses import dataclass


@dataclass
class RetrieveToken:
    client_host: str
    agent: str
    accept_language: str
    username: str
    password: str