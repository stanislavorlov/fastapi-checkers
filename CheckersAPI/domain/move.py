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

class CapturedMove(Move):
    def __init__(self, from_: str, to: str, captured_at: str):
        super().__init__(from_, to)
        self._captured_at = captured_at
        
    @property
    def captured_at(self):
        return self._captured_at