import time
import random
from pydantic import NameEmail, Field, EmailStr, model_validator
from domain.kernel.value_object import ValueObject

class Contact(ValueObject):
    contact: NameEmail = Field(default_factory=lambda: Contact.default_contact())
    email: EmailStr | None = None
    username: str | None = None

    @model_validator(mode="after")
    def fill_username_email(self):
        self.email = self.contact.email
        self.username = self.contact.name

        return self

    @staticmethod
    def default_contact():
        ticks = int(time.time() * 1000)  # current time in milliseconds
        rand = random.randint(100, 999)  # optional random digits for uniqueness
        name = f"guest{ticks}{rand}"

        return NameEmail(name=name, email=f"{name}@checkers.com")

contact1 = Contact(contact="stasorlov21 <stasorlov21@gmail.com>")
print(contact1.email)
temp: str = contact1.email
print(temp)
print(contact1.username)
#
# contact2 = Contact()
# print(contact2.email)
# print(contact2.username)