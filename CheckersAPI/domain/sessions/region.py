from domain.kernel.value_object import ValueObject
from pydantic import model_validator


class Region(ValueObject):
    code: str

    @model_validator(mode='after')
    def validate_region(self) -> 'Region':
        allowed = {"EU", "NA", "AS", "AF", "OC"}
        if self.code not in allowed:
            raise ValueError(f"Invalid region: {self.code}")
        return self

    @staticmethod
    def eu():
        return Region("EU")

    @staticmethod
    def na():
        return Region("NA")

    @staticmethod
    def as_():
        return Region("AS")

    @staticmethod
    def af():
        return Region("AF")

    @staticmethod
    def oc():
        return Region("OC")