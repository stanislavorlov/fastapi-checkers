import numpy as np
from domain.board.board import Board
from domain.side import Side


class TensorHelper:

    @staticmethod
    def board_to_8_8_3_tensor(board: Board):
        tensor = np.zeros([8, 8, 3])

        for i in range(1, 33):
            piece = board.get_piece(i)
            if piece:
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

    @staticmethod
    def board_to_8_4_5_tensor(board: Board):
        tensor = np.zeros([8, 4, 5])

        for i in range(1, 33):
            piece = board.get_piece(i)
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

    @staticmethod
    def board_as_sdfen(board: Board):
        turn = "B" if board.turn == Side.Dark else "W"
        black_pieces = ''
        white_pieces = ''

        for i in range(1, 33):
            match board.get_piece(i):
                case 'b':
                    black_pieces += f"b{i},"
                case 'B':
                    black_pieces += f"B{i},"
                case 'w':
                    white_pieces += f"w{i},"
                case 'W':
                    white_pieces += f"W{i},"

        return f"{turn}:{black_pieces.rstrip(",")}:{white_pieces.rstrip(",")}"