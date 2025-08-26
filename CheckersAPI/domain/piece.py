from domain.board import Directions
from domain.color import Color


class Piece:
    def __init__(self, color: Color):
        self._color = color

    @property
    def color(self):
        return self._color

    def get_move_directions(self):
        return [Directions.DOWN_LEFT, Directions.DOWN_RIGHT] \
            if self._color == Color.Black \
            else [Directions.UP_RIGHT, Directions.UP_LEFT]
