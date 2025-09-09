class LegalMove:
    def __init__(self, from_: int, to_: int):
        self.from_ = from_
        self.to_ = to_

    def __repr__(self):
        return f"({self.from_}, {self.to_})"

class CapturedMove(LegalMove):
    def __init__(self, from_: int, to_: int, jumped: int):
        super().__init__(from_, to_)
        self.jumped = jumped