from dataclasses import dataclass
from domain.kernel.value_object import ValueObject


@dataclass
class Region(ValueObject):
    code: str

    def __post_init__(self):
        allowed = {"EU", "NA", "AS", "AF", "OC"}
        if self.code not in allowed:
            raise ValueError(f"Invalid region: {self.code}")

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