from dataclasses import dataclass, field
from typing import List
from domain.kernel.aggregate_root import AggregateRoot
from domain.players.player import Player
from domain.users.full_name import FirstName, LastName, FullName
from domain.users.user_session import UserSession
from web.user_helper import nanoid, hash_password

@dataclass
class User(AggregateRoot):
    user_id: str
    first_name: FirstName
    last_name: LastName
    country: str
    email: str
    password_hash: str
    player: Player
    sessions: List[UserSession] = field(default_factory=list)

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    @staticmethod
    def create(full_name: FullName, country: str, email: str, password: str, player: Player) -> "User":
        user = User(
            user_id=nanoid(10),
            first_name=full_name.first,
            last_name=full_name.last,
            country=country,
            email=email,
            player=player,
            password_hash=hash_password(password),
        )

        return user

    def start_session(self, session_token: str, host: str, agent: str) -> UserSession:
        session = UserSession.create(session_token=session_token, anonymous=False, host=host, agent=agent)
        self.sessions.append(session)

        return session

    def end_session(self, session_id):
        session = next((item for item in self.sessions if item.id == session_id), None)

        if session:
            self.sessions.remove(session)

    def get_active_sessions(self) -> List[UserSession]:
        return self.sessions