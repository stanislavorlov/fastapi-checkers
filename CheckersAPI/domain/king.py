from domain.side import Side
from domain.man import Man


class King(Man):
    def __init__(self, color: Side):
        super().__init__(color)
