from typing import Optional
from pydantic import Field
from domain.kernel.value_object import ValueObject
from domain.profile.contact import Contact


class DisplayName(ValueObject):
    display_name: Optional[str] = Field(None, alias="display_name")

    @property
    def value(self) -> str:
        return self.display_name

    @staticmethod
    def from_contact(contact: Contact) -> "DisplayName":
        return DisplayName(display_name=contact.username)