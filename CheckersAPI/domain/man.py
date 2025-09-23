from domain.side import Side


class Man:
    def __init__(self, color: Side):
        self._color = color

    @property
    def color(self):
        return self._color
