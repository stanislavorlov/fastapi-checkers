from dataclasses import dataclass

@dataclass
class RegisterProfileRequest:
    email: str
    password: str
    first_name: str
    last_name: str
    level: str
    language: str
    country: str
