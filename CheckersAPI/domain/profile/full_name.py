import uuid
from domain.kernel.value_object import ValueObject


class FirstName(ValueObject):
    value: str

    @staticmethod
    def create(value: str | None = None) -> "FirstName":
        if not value or not value.strip():
            value = "Anonymous"
        return FirstName(value=value.strip())

    def __str__(self):
        return self.value


class LastName(ValueObject):
    value: str

    @staticmethod
    def create(value: str | None = None) -> "LastName":
        if not value or not value.strip():
            suffix = uuid.uuid4().hex[:5].upper()
            value = f"Player-{suffix}"
        return LastName(value=value.strip())

    def __str__(self):
        return self.value

class FullName(ValueObject):
    first: FirstName
    last: LastName

    @staticmethod
    def create(first: str | None, last: str | None) -> "FullName":
        return FullName(
            first=FirstName.create(first),
            last=LastName.create(last),
        )

    def __str__(self):
        return f"{self.first} {self.last}"