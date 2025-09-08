# ToDo: board into Tensor (32 cells array)
# Predict next movement based on current position (FEN) and game result

from collections import defaultdict
from enum import Enum
import tensorflow as tf
from keras import Model
from keras.layers import Dense, Input, Dropout, Flatten
import numpy as np
import pandas as pd
from keras.src.layers import Conv2D, Softmax


class GameResult(Enum):
    BLACK_WIN = 1
    DRAW = 0
    WHITE_WIN = -1


def square_to_coords(sq: int):
    """Convert 1–32 square number to (row, col) on 8×8 board."""
    row = (sq - 1) // 4
    k = (sq - 1) % 4
    col = 2 * k + (1 if row % 2 == 0 else 0)
    return row, col

def coords_to_square(row: int, col: int):
    """Convert (row, col) on 8×8 board back to 1–32 square number."""
    k = (col - (1 if row % 2 == 0 else 0)) // 2
    return row * 4 + k + 1

def captured_square(start: int, end: int):
    """Return the captured square between start and end (single jump)."""
    r1, c1 = square_to_coords(start)
    r2, c2 = square_to_coords(end)

    # midpoint of the diagonal
    rm, cm = (r1 + r2) // 2, (c1 + c2) // 2

    return coords_to_square(rm, cm)

class Game:
    def __init__(self, game_id: int, result: GameResult):
        self._id = game_id
        self._result = result
        self._turn = 1  # black: 1, white: -1

        self._board = defaultdict()
        for i in range(1,33):
            if i <= 12:
                self._board[i] = "b"
            elif i >= 21:
                self._board[i] = "w"
            else:
                self._board[i] = ""

    def register_move(self, move: str):
        # 11-15
        # 10x17
        # 6x13x22
        move = move.strip()
        sep = "x" if "x" in move else "-"
        squares = [int(x.strip().strip('"')) for x in move.split(sep)]
        from_ = squares[0]
        piece = self._board[from_]
        self._board[from_] = ""
        for sq in squares[1:]:
            if "x" in move:
                captured = captured_square(from_, sq)
                self._board[captured] = ""
            from_ = sq
        self._board[from_] = piece
        self._turn = 1 if self._turn == -1 else -1

    def get_sdfen(self):
        turn = "B" if self._turn == 1 else "W"
        black_pieces = ''
        white_pieces = ''

        for i in range(1, 33):
            match self._board[i]:
                case 'b':
                    black_pieces += f"b{i},"
                case 'w':
                    white_pieces += f"w{i},"

        return f"{turn}:{black_pieces.rstrip(",")}:{white_pieces.rstrip(",")}"

    def board_to_tensor(self):
        """Converts checkers board in SDFEN format into compact tensor shape (8,4,5).
        In case of AlphaZero CNN architecture, a full tensor shape (8,8,C) to be used.
        Channels: black man, black king, white man, white king, side-to-move.
        Example SDFEN: B:b1,b2,b3,b4,b5,b6,b7,b8,b9,b10,b11,b12:w21,w22,w23,w24,w25,w26,w27,w28,w29,w30,w31,w32"""

        def board_square_to_rc(sq):
            if not 1 <= sq <= 32:
                return None

            """Convert square index 1–32 into (row, col) in (8,4) grid"""
            row = (sq - 1) // 4
            col = (sq - 1) % 4

            return (row, col)

        side, black_pieces, white_pieces = self.get_sdfen().split(":")

        # 8 rows * 4 cells and 5 channels [black_man, black_king, white_man, white_king, side_to_move]
        tensor = np.zeros([8, 4, 5])

        for piece in black_pieces.split(","):
            if piece:
                sq = int(piece[1:])     # b12 -> 12
                r,c = board_square_to_rc(sq)
                if piece[0].islower():
                    tensor[r, c, 0] = 1     # black man
                else:
                    tensor[r, c, 1] = 1     # black king

        for piece in white_pieces.split(","):
            if piece:
                sq = int(piece[1:])     # w12 -> 12
                r,c = board_square_to_rc(sq)
                if piece[0].islower():
                    tensor[r, c, 2] = 1     # white man
                else:
                    tensor[r, c, 3] = 1     # white king

        tensor[:, :, 4] = 1 if side == "B" else 0

        return tensor

def build_checkers_model(input_shape=(8, 4, 5), policy_size=256):
    """
    AlphaZero-style network for checkers.
    input_shape: (8, 4, 5)
    policy_size: number of possible moves in fixed action space
    """

    inputs = Input(shape=input_shape)

    # Shared convolutional trunk
    x = Conv2D(64, (3, 3), padding="same", activation="relu")(inputs)
    x = Conv2D(64, (3, 3), padding="same", activation="relu")(x)
    x = Conv2D(128, (3, 3), padding="same", activation="relu")(x)
    x = Flatten()(x)
    x = Dense(256, activation="relu")(x)

    # Policy head
    policy_logits = Dense(policy_size, activation=None, name="policy")(x)
    policy_out = Softmax(name="policy_output")(policy_logits)

    # Value head
    v = Dense(64, activation="relu")(x)
    value_out = Dense(1, activation="tanh", name="value_output")(v)

    # Model
    model = Model(inputs=inputs, outputs=[policy_out, value_out])

    # Losses: categorical for policy, MSE for value
    model.compile(
        optimizer=tf.keras.optimizers.Adam(1e-3),
        loss={
            "policy_output": "categorical_crossentropy",
            "value_output": "mean_squared_error"
        },
        loss_weights={
            "policy_output": 1.0,
            "value_output": 1.0
        }
    )

    return model

if __name__ == '__main__':

    df = pd.read_csv('../games.csv', sep=';')

    for index, row in df.iterrows():
        print(f"{row['game_id']}\t{row['result']}\t{row['moves']}")

        match row['result']:
            case 'white_win':
                game_result = GameResult.WHITE_WIN
            case 'black_win':
                game_result = GameResult.BLACK_WIN
            case _:
                game_result = GameResult.DRAW

        game = Game(row['game_id'], game_result)
        moves = str(row['moves']).split(',')
        for m in moves:
            game.register_move(m)

        model = build_checkers_model(input_shape=(8, 4, 5), policy_size=256)
        model.summary()

        if index == 5:
            break