from domain.color import Color


class Piece:
    def __init__(self, color: Color):
        self._color = color

    @property
    def color(self):
        return self._color
