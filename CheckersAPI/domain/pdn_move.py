class PdnMove:

    def __init__(self, pdn_string: str, captured: list[str]):
        self._pdn_string = pdn_string
        self._captured = captured
        self._captured_idx = 0

        self.__validate_captured_squares(pdn_string, captured)

    @property
    def as_string(self):
        return self._pdn_string

    @property
    def move_squares(self):
        return self.__parse_move(str(self._pdn_string))

    @property
    def captured_squares(self):
        return self._captured

    @property
    def next_captured_square(self):
        if len(self._captured) and self._captured_idx < len(self._captured):
            item = self._captured[self._captured_idx]
            self._captured_idx += 1

            return item

        return None

    def to_dict(self) -> dict:
        return {
            "pdn" : self._pdn_string,
            "captured" : self._captured,
        }

    @staticmethod
    def __parse_move(move_str: str):
        sep = "x" if "x" in move_str else "-"
        try:
            return [int(x.strip().strip('"')) for x in move_str.split(sep)]
        except ValueError:
            return []

    @staticmethod
    def __square_to_coord(square: int) -> tuple[int, int]:
        """Convert 1–32 index into (row, col) on 8×8 board."""
        row = (square - 1) // 4
        col_in_row = (square - 1) % 4
        if row % 2 == 0:  # even row: dark squares at cols 1,3,5,7
            col = col_in_row * 2 + 1
        else:  # odd row: dark squares at cols 0,2,4,6
            col = col_in_row * 2
        return row, col

    @staticmethod
    def __coord_to_square(row: int, col: int) -> int:
        """Convert (row, col) back into 1–32 index."""
        if row % 2 == 0:
            col_in_row = (col - 1) // 2
        else:
            col_in_row = col // 2
        return row * 4 + col_in_row + 1

    @staticmethod
    def __validate_captured_squares(pdn_string: str, captured_squares: list[str]):
        if len(captured_squares) > 0:
            # raises error if x not found for captured move
            pdn_string.index("x")

            parsed_squares = PdnMove.__parse_move(pdn_string)
            if not len(parsed_squares):
                raise ValueError("Could not parse pdn move")

            from_ = parsed_squares[0]
            capture_idx = 0
            for sq in parsed_squares[1:]:
                to = sq
                r1, c1 = PdnMove.__square_to_coord(from_)
                r2, c2 = PdnMove.__square_to_coord(to)
                rm, cm = (r1 + r2) // 2, (c1 + c2) // 2

                jumped = PdnMove.__coord_to_square(rm, cm)
                if jumped != int(captured_squares[capture_idx]):
                    raise ValueError("Captured squares are invalid")
                capture_idx += 1

                from_ = to