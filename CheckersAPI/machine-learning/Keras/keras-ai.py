import keras

EMPTY = 0
P1_MAN = 1
P1_KING = 2
P2_MAN = -1
P2_KING = -2

import numpy as np


def initial_board():
    """Standard 8x8 checkers setup with 32 playable squares."""
    board = [0] * 32
    # Player 1 pieces (top)
    for i in range(12):
        board[i] = P2_MAN
    # Player 2 pieces (bottom)
    for i in range(20, 32):
        board[i] = P1_MAN
    return board

# === Move parsing ===
def parse_move(move_str):
    move_str = move_str.strip()
    move_str = move_str.strip('"')
    """Split move into sequence of ints."""
    sep = "x" if "x" in move_str else "-"
    try:
        return [int(x.strip().strip('"')) for x in move_str.split(sep)]
    except ValueError:
        return []

# === Apply move ===
def apply_move(board: list[int], move: str, player: int):
    """Update board after a move, return new board."""
    new_board = board[:]
    squares = parse_move(move)
    frm = squares[0] - 1  # 0-indexed
    piece = new_board[frm]
    new_board[frm] = EMPTY
    for sq in squares[1:]:
        to = sq - 1
        # if capture
        if abs(to - frm) > 5:  # crude check for jump
            jumped = (frm + to) // 2
            new_board[jumped] = EMPTY
        frm = to
    new_board[to] = piece
    return new_board

# === Move dictionary (all seen moves) ===
move_to_idx, idx_to_move = {}, []

def register_move(move):
    if move not in move_to_idx:
        move_to_idx[move] = len(idx_to_move)
        idx_to_move.append(move)

# === Build dataset ===
def build_dataset(games: list[list[str]]):
    X, y = [], []
    for game in games:
        board = initial_board()
        player = P2_MAN  # first move is black in PDN
        for move in game:
            if move != '\n':
                register_move(move)
                X.append(board[:])
                y.append(move_to_idx[move])
                board = apply_move(board, move, player)
                player *= -1  # switch players
    return np.array(X), np.array(y)

# === Example games ===
# games = [
#     ["11-15", "24-20", "8-11", "28-24"],
#     ["19x12", "10-15", "11-8", "15-18"]
# ]

games: list[list[str]] = []
with open('moves.txt', 'r') as f:
    for line in f:
        games.append(line.split(','))

X, y = build_dataset(games)

print("X shape:", X.shape, "y shape:", y.shape)
print("Unique moves:", len(move_to_idx))

num_squares = 32
num_moves = len(move_to_idx)

# model = models.Sequential([
#     layers.Input(shape=(num_squares,)),
#     layers.Embedding(input_dim=5, output_dim=8, input_length=num_squares),  # -2..2 → 0..4 remap needed
#     layers.Flatten(),
#     layers.Dense(128, activation="relu"),
#     layers.Dense(128, activation="relu"),
#     layers.Dense(num_moves, activation="softmax")
# ])
#
# model.compile(optimizer="adam",
#               loss="sparse_categorical_crossentropy",
#               metrics=["accuracy"])
#
# model.fit(X, y, batch_size=32, epochs=10, validation_split=0.1)
#
# model.save('model.keras')
model = keras.models.load_model('model.keras')

# men: 1,-1 kings: 2,-2
board = X[0].reshape(1, -1)
print(board)
pred = model.predict(board)
move = idx_to_move[np.argmax(pred)]
print("Predicted move:", move)
