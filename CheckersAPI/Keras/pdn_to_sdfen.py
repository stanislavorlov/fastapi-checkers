from typing import List, Tuple


# --- Helpers ---
def build_mappings():
    num_to_coord = {}
    coord_to_num = {}
    n = 1
    for r in range(8):
        for c in range(8):
            if (r + c) % 2 == 1:  # dark square
                num_to_coord[n] = (r, c)
                coord_to_num[(r, c)] = n
                n += 1
    return num_to_coord, coord_to_num


NUM_TO_COORD, COORD_TO_NUM = build_mappings()


def init_board():
    board = {}
    for i in range(1, 13):
        board[i] = 'b'  # black man
    for i in range(21, 33):
        board[i] = 'w'  # white man
    return board


def apply_move(board, move: str, side: str, move_index: int):
    print(f"Move {move_index + 1} ({'Black' if side == 'B' else 'White'}): {move}")

    parts = move.replace('x', '-').split('-')
    squares = list(map(int, parts))

    src = squares[0]
    dst = squares[-1]

    if src not in board:
        raise KeyError(f"Invalid move: no piece at square {src} for move {move}")

    piece = board.pop(src)

    # If capture move, remove jumped pieces
    if 'x' in move:
        for i in range(len(squares) - 1):
            a, b = squares[i], squares[i + 1]
            ra, ca = NUM_TO_COORD[a]
            rb, cb = NUM_TO_COORD[b]
            rc, cc = (ra + rb) // 2, (ca + cb) // 2
            captured = COORD_TO_NUM[(rc, cc)]
            if captured in board:
                print(f"  Capturing piece at {captured}")
                del board[captured]

    # Promotion
    r, _ = NUM_TO_COORD[dst]
    if piece == 'b' and r == 7:
        piece = 'B'
    if piece == 'w' and r == 0:
        piece = 'W'

    board[dst] = piece
    print(f"  Moved {piece} to {dst}")
    print(f"  Board now: {dict(sorted(board.items()))}")
    print(f"  Board FEN: {board_to_sdfen(board, side)}\n")

    return board


def board_to_sdfen(board, side):
    blacks, whites = [], []
    for sq, piece in sorted(board.items()):
        if piece == 'b':
            blacks.append(f"b{sq}")
        elif piece == 'B':
            blacks.append(f"B{sq}")
        elif piece == 'w':
            whites.append(f"w{sq}")
        elif piece == 'W':
            whites.append(f"W{sq}")
    return f"{side}:{','.join(blacks)}:{','.join(whites)}"


def pdn_to_sdfen(moves: List[str]) -> str:
    board = init_board()
    side = 'B'
    for i, move in enumerate(moves):
        board = apply_move(board, move, side, i)
        side = 'W' if side == 'B' else 'B'
    final = board_to_sdfen(board, side)
    print("Final SDFEN:", final)
    return final


# Example moves
moves = ["11-15", "24-20", "8-11", "28-24", "9-13", "22-18",
         "15x22", "25x18", "4-8", "26-22", "10-14", "18x9",
         "5x14", "22-18", "1-5", "18x9", "5x14", "29-25",
         "11-15", "24-19", "15x24", "25-22", "24-28", "22-18",
         "6-9", "27-24", "8-11", "24-19", "7-10", "20-16",
         "11x20", "18-15", "2-6", "15-11", "12-16", "19x12",
         "10-15", "11-8", "15-18", "21-17", "13x22", "30-26",
         "18x27", "26x17x10x1"]

# FEN:
# rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1
# w - current turn, KQkq - castling availability (black and white), - no en passant capture, 0 half moves, 1 full move

pdn_to_sdfen(moves)

# SDFEN:
# B:b3,b9,b20,b27,b28:W1,w8,w12,w31,w32
# B -> black to move
# black men occupy 3,9,20,27
# white men occupy 8,12,31,31
# white King occupy 1