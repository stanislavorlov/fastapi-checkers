class BoardHelper:

    @staticmethod
    def captured_square(start: int, end: int):
        """Return the captured square between start and end (single jump)."""
        r1, c1 = BoardHelper.square_to_position(start)
        r2, c2 = BoardHelper.square_to_position(end)

        # midpoint of the diagonal
        rm, cm = (r1 + r2) // 2, (c1 + c2) // 2

        return BoardHelper.position_to_square(rm, cm)

    @staticmethod
    def square_to_position(square: int) -> tuple[int, int]:
        """
        Map 1–32 to board positions (row, col)
        """

        if not 1 <= square <= 32:
            raise ValueError("Square must be in 1..32")
        row = (square - 1) // 4
        col = 2 * ((square - 1) % 4) + ((row + 1) % 2)
        return row, col

    @staticmethod
    def position_to_square(row: int, col: int) -> int:
        if (row + col) % 2 == 0:
            raise ValueError("Invalid position: not a playable square")
        index_in_row = col // 2
        return row * 4 + index_in_row + 1