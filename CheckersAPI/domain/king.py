from domain.piece import Piece
from domain.side import Side


class King(Piece):

    @property
    def is_king(self):
        return True

    @property
    def is_man(self):
        return False

    def __init__(self, color: Side):
        super().__init__(color)

    @property
    def acronym(self):
        return self._color.value.upper()

    @property
    def jump_directions(self) -> list[tuple[int, int]]:
        return [(-1, -1), (-1, 1), (1, -1), (1, 1)]