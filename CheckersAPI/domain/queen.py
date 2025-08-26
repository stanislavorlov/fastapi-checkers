from domain.board import Directions
from domain.color import Color
from domain.piece import Piece


class Queen(Piece):
    def __init__(self, color: Color):
        super().__init__(color)

    def get_move_directions(self):
        return [Directions.DOWN_LEFT, Directions.DOWN_RIGHT, Directions.UP_RIGHT, Directions.UP_LEFT]
