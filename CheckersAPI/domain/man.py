from domain.piece import Piece
from domain.side import Side


class Man(Piece):

    @property
    def is_king(self):
        return False

    @property
    def is_man(self):
        return True

    def __init__(self, color: Side):
        super().__init__(color)

    @property
    def acronym(self):
        return self._color.value.lower()

    @property
    def jump_directions(self) -> list[tuple[int, int]]:
        if self._color == Side.Dark:
            return [(1, -1), (1, 1)]
        return [(-1, -1), (-1, 1)]