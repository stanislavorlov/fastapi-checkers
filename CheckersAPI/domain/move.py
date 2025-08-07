class Move:

    def __init__(self, from_: str, to: str):
        self._from = from_
        self._to = to

    @property
    def from_(self):
        return self._from

    @property
    def to(self):
        return self._to
