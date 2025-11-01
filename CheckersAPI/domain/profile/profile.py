from datetime import datetime, timezone
from typing import Optional
from pydantic import EmailStr, Field
from domain.profile.full_name import FirstName, LastName
from domain.kernel.aggregate_root import AggregateRoot


class Profile(AggregateRoot):
    email: EmailStr
    password_hash: str
    username: str
    locked: bool = False
    join_date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    first_name: Optional[FirstName] = None
    last_name: Optional[LastName] = None
    language: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    country: Optional[str] = None

    # ---- Domain Behaviors ----

    def lock(self):
        """Lock the account (e.g., admin action)."""
        if self.locked:
            raise ValueError("Account already locked.")
        self.locked = True

    def unlock(self):
        """Unlock the account."""
        if not self.locked:
            raise ValueError("Account is not locked.")
        self.locked = False

    def rename(self, new_username: str):
        """Change username if an account is not locked."""
        if self.locked:
            raise PermissionError("Cannot rename a locked account.")
        if not new_username or len(new_username) < 3:
            raise ValueError("Username must be at least 3 characters long.")
        self.username = new_username

    def update_profile(self, **kwargs):
        """Update editable profile fields."""
        if self.locked:
            raise PermissionError("Cannot update profile when locked.")

        editable = {"first_name", "last_name", "language", "bio", "avatar_url", "country"}
        for field, value in kwargs.items():
            if field in editable:
                setattr(self, field, value)