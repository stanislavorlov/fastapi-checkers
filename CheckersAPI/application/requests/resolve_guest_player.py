from dataclasses import dataclass

@dataclass
class ResolveGuestPlayerRequest:
    host: str
    agent: str
