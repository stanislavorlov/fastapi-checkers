from datetime import datetime, timezone
from typing import Optional
from pydantic import Field
from domain.kernel.aggregate_root import AggregateRoot
from domain.profile.contact import Contact
from domain.profile.full_name import FullName


class Profile(AggregateRoot):
    password_hash: str
    contact: Contact
    locked: bool = False
    initial_level: str
    join_date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    full_name: Optional[FullName] = None
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

    # def rename(self, new_username: str):
    #     """Change username if an account is not locked."""
    #     if self.locked:
    #         raise PermissionError("Cannot rename a locked account.")
    #     if not new_username or len(new_username) < 3:
    #         raise ValueError("Username must be at least 3 characters long.")
    #     self.username = new_username

    def update_profile(self, **kwargs):
        """Update editable profile fields."""
        if self.locked:
            raise PermissionError("Cannot update profile when locked.")

        # Fields that can be set directly via setattr
        direct_editable = {"language", "bio", "avatar_url", "country"}
        
        # Handle FullName update
        first = self.full_name.first.value if self.full_name else None
        last = self.full_name.last.value if self.full_name else None
        
        name_updated = False
        if "first_name" in kwargs:
            first = kwargs["first_name"]
            name_updated = True
        if "last_name" in kwargs:
            last = kwargs["last_name"]
            name_updated = True
            
        if name_updated:
            self.full_name = FullName.create(first, last)

        # Handle Contact update
        if "email" in kwargs or "username" in kwargs:
            email = kwargs.get("email", self.contact.email)
            username = kwargs.get("username", self.contact.username)
            self.contact = Contact(contact=f"{username} <{email}>")

        # Handle direct fields
        for field, value in kwargs.items():
            if field in direct_editable:
                setattr(self, field, value)