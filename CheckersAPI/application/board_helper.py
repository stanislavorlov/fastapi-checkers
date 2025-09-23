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

    # noinspection PyChainedComparisons
    @staticmethod
    def generate_maps():
        """Generate MOVE_MAP and CAPTURE_MAP automatically for 32 squares."""
        move_map, capture_map = {}, {}
        board = [[0] * 8 for _ in range(8)]
        square = 1
        for row in range(8):
            for col in range(8):
                if (row + col) % 2 == 1:  # dark square
                    board[row][col] = square
                    square += 1

        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        for row in range(8):
            for col in range(8):
                square = board[row][col]
                if square == 0: continue
                move_map[square] = []
                capture_map[square] = []
                for dr, dc in directions:
                    nr, nc = row + dr, col + dc
                    if 0 <= nr < 8 and 0 <= nc < 8 and board[nr][nc] != 0:
                        move_map[square].append((board[nr][nc], None))
                    jr, jc = row + 2 * dr, col + 2 * dc
                    if (0 <= jr < 8 and 0 <= jc < 8
                            and board[nr][nc] != 0 and board[jr][jc] != 0):
                        capture_map[square].append((board[nr][nc], board[jr][jc]))

        return move_map, capture_map