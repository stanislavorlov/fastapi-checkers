from abc import ABC, abstractmethod
from domain.side import Side


class Piece(ABC):
    def __init__(self, color: Side):
        self._color = color

    @property
    def color(self) -> Side:
        return self._color

    @property
    @abstractmethod
    def acronym(self) -> str:
        ...

    @property
    @abstractmethod
    def is_man(self):
        ...

    @property
    @abstractmethod
    def is_king(self):
        ...

    @property
    @abstractmethod
    def jump_directions(self) -> list[tuple[int, int]]:
        ...