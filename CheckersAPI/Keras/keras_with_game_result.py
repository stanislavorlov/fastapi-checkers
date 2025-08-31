# This is exactly how AlphaZero-style checkers/chess engines are trained:
#       Policy head → predicts the move distribution.
#       Value head → predicts game outcome from that position.

# So dataset will be:
#   X → board (with turn encoded)
#   y_policy → move index (one-hot / sparse)
#   y_value → outcome (1 = win, -1 = lose, 0 = draw)

EMPTY = 0
P1_MAN = 1
P1_KING = 2
P2_MAN = -1
P2_KING = -2

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

# === Move dictionary (all seen moves) ===
move_to_idx, idx_to_move = {}, []

def register_move(move):
    if move not in move_to_idx:
        move_to_idx[move] = len(idx_to_move)
        idx_to_move.append(move)

def build_dataset(games_with_results):
    """
    games_with_results = [
        (["11-15", "24-20", ...], 1),   # 1 = P1 win
        (["19x12", "10-15", ...], -1),  # -1 = P2 win
        (["11-15", "22-18", ...], 0)    # 0 = draw
    ]
    """
    X, policy, value = [], [], []
    for moves, result in games_with_results:
        board = initial_board()
        player = P2_MAN  # PDN starts with black
        for move in moves:
            register_move(move)

            # Encode turn separately (extra feature)
            state = board[:] + [1 if player == P1_MAN else -1]

            X.append(state)
            policy.append(move_to_idx[move])

            # perspective: if current player eventually won, reward=1
            val = result if player == P1_MAN else -result
            value.append(val)

            board = apply_move(board, move, player)
            player *= -1
    return np.array(X), np.array(policy), np.array(value)

num_squares = 33  # 32 squares + 1 turn
num_moves = len(move_to_idx)

inp = layers.Input(shape=(num_squares,))
x = layers.Dense(128, activation="relu")(inp)
x = layers.Dense(128, activation="relu")(x)

# Policy head
policy_out = layers.Dense(num_moves, activation="softmax", name="policy")(x)

# Value head
value_out = layers.Dense(1, activation="tanh", name="value")(x)  # range [-1, 1]

model = models.Model(inputs=inp, outputs=[policy_out, value_out])

model.compile(
    optimizer="adam",
    loss={
        "policy": "sparse_categorical_crossentropy",
        "value": "mse"
    },
    loss_weights={"policy": 1.0, "value": 0.5},
    metrics={"policy": "accuracy", "value": "mse"}
)

games_with_results = [
    (["11-15", "24-20", "8-11", "28-24"], 1),   # P1 win
    (["19x12", "10-15", "11-8", "15-18"], -1)   # P2 win
]

X, y_policy, y_value = build_dataset(games_with_results)

model.fit(
    X,
    {"policy": y_policy, "value": y_value},
    batch_size=32,
    epochs=10,
    validation_split=0.1
)
