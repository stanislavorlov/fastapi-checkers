from dataclasses import dataclass
from domain.kernel.value_object import ValueObject


@dataclass(frozen=True)
class Region(ValueObject):
    name: str

    @staticmethod
    def global_():
        return Region("global")

    @staticmethod
    def uk():
        return Region("uk")

    @staticmethod
    def europe():
        return Region("EU")