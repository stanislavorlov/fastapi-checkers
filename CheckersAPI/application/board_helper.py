import numpy as np
from domain.board import Board
from domain.color import Color


def captured_square(start: int, end: int):
    """Return the captured square between start and end (single jump)."""
    r1, c1 = square_to_position(start)
    r2, c2 = square_to_position(end)

    # midpoint of the diagonal
    rm, cm = (r1 + r2) // 2, (c1 + c2) // 2

    return position_to_square(rm, cm)

def board_to_8_8_3_tensor(board: Board):
    tensor = np.zeros([8, 8, 3])

    for i in range(1, 33):
        piece = board.piece_at(i)
        if len(piece):
            r = (i - 1) // 4
            c = 2 * ((i - 1) % 4) + (1 if r % 2 == 0 else 0)

            match piece:
                case 'b':
                    tensor[r, c, 1] = 1.0
                case 'B':
                    tensor[r, c, 1] = 1.0
                    tensor[r, c, 2] = 1.0
                case 'w':
                    tensor[r, c, 0] = 1.0
                case 'W':
                    tensor[r, c, 0] = 1.0
                    tensor[r, c, 2] = 1.0

    return tensor

def board_to_8_4_5_tensor(board: Board):
    tensor = np.zeros([8, 4, 5])

    for i in range(1, 33):
        piece = board.piece_at(i)
        if len(piece):
            row = (i - 1) // 4
            col = (i - 1) % 4

            match piece:
                case 'b':
                    tensor[row, col, 0] = 1.0
                case 'B':
                    tensor[row, col, 1] = 1.0
                case 'w':
                    tensor[row, col, 2] = 1.0
                case 'W':
                    tensor[row, col, 3] = 1.0

    return tensor

# Map 1–32 to board positions (row, col)
def square_to_position(square: int) -> tuple[int, int]:
    if not 1 <= square <= 32:
        raise ValueError("Square must be in 1..32")
    row = (square - 1) // 4
    col = 2 * ((square - 1) % 4) + ((row + 1) % 2)
    return row, col

def position_to_square(row: int, col: int) -> int:
    if (row + col) % 2 == 0:
        raise ValueError("Invalid position: not a playable square")
    index_in_row = col // 2
    return row * 4 + index_in_row + 1

def board_as_sdfen(board: Board):
    turn = "B" if board.turn == Color.Black else "W"
    black_pieces = ''
    white_pieces = ''

    for i in range(1, 33):
        match board.piece_at(i):
            case 'b':
                black_pieces += f"b{i},"
            case 'B':
                black_pieces += f"B{i},"
            case 'w':
                white_pieces += f"w{i},"
            case 'W':
                white_pieces += f"W{i},"

    return f"{turn}:{black_pieces.rstrip(",")}:{white_pieces.rstrip(",")}"