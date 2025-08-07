from domain.color import Color
from domain.piece import Piece


class Queen(Piece):
    def __init__(self, color: Color):
        super().__init__(color)
