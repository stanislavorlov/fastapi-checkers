from collections import defaultdict
from enum import Enum
import numpy as np
from domain.color import Color
from domain.legal_move import LegalMove
from domain.move import Move
from domain.node import Node
from domain.piece import Piece
from domain.queen import Queen

class Directions(Enum):
    UP_LEFT = (-1,-1)
    UP_RIGHT = (-1,1)
    DOWN_LEFT = (1,-1)
    DOWN_RIGHT = (1,1)

# Map 1–32 to board positions (row, col)
def square_to_position(square: int) -> tuple[int, int]:
    if not 1 <= square <= 32:
        raise ValueError("Square must be in 1..32")
    row = (square - 1) // 4
    col = 2 * ((square - 1) % 4) + ((row + 1) % 2)
    return row, col

# Reverse mapping
def position_to_square(row: int, col: int) -> int:
    if (row + col) % 2 == 0:
        raise ValueError("Invalid position: not a playable square")
    index_in_row = col // 2
    return row * 4 + index_in_row + 1


class Board:

    def __init__(self):
        self._turn = Color.Black
        self.red_pieces = 12
        self.black_pieces = 12
        self._board = {i: Node(i) for i in range(1, 33)}

        for square, node in self._board.items():
            row, col = square_to_position(square)

            if square <= 12:
                node.piece = Piece(Color.Black)
            elif square >= 21:
                node.piece = Piece(Color.Red)

            for direction in Directions:
                dr, dc = direction.value
                r2, c2 = row + dr, col + dc
                if 0 <= r2 < 8 and 0 <= c2 < 8:
                    try:
                        neighbor_square = position_to_square(r2, c2)
                        neighbor = self._board[neighbor_square]
                        node.add_neighbor(direction, neighbor)
                    except ValueError:
                        pass  # skip invalid (non-playable) squares

    def display(self):
        board_view = [["⬜" if (r + c) % 2 == 0 else "⬛" for c in range(8)] for r in range(8)]

        for square, node in self._board.items():
            row, col = square_to_position(square)
            if hasattr(node, "piece") and node.piece:
                board_view[row][col] = '⚫' if node.piece.color == Color.Black else '🔴'
            else:
                board_view[row][col] = "⬛"

        print("  A B  C D E F G H")
        for i, row in enumerate(board_view):
            print(f"{8 - i} " + "".join(row) + f" {8 - i}")
        print("  A B  C D E F G H")

    @property
    def turn(self):
        return self._turn

    def get_piece(self, pos: int) -> Piece:
        if 1 <= pos <= 32:
            node = self._board[pos]

            return node.piece

        return None

    def move_piece(self, move: Move):
        node_from = self._board[int(move.from_)]
        node_to = self._board[int(move.to)]

        node_to.piece = node_from.piece
        node_from.piece = None

        # ToDo: detect capture and promotion

        # if abs(sr - er) == 2:
        #     captured_r, captured_c = (sr + er) // 2, (sc + ec) // 2
        #     captured_piece = self.get_piece(captured_r, captured_c)
        #
        #     self.board[captured_r][captured_c] = EMPTY
        #     if captured_piece == BLACK_PIECE or captured_piece == BLACK_KING:
        #         self.black_pieces -= 1
        #     elif captured_piece == RED_PIECE or captured_piece == RED_KING:
        #         self.red_pieces -= 1
        #
        # if piece == RED_PIECE and er == 7:
        #     self.board[er][ec] = RED_KING
        # elif piece == BLACK_PIECE and er == 0:
        #     self.board[er][ec] = BLACK_KING

        self._turn = Color.Black if self._turn == Color.Red else Color.Red

    def copy(self):
        new_board = Board()
        new_board._board = self._board.copy()
        new_board._turn = self.turn

        return new_board

    def get_state_representation(self):
        state = np.zeros((8, 8, 3), dtype=np.float32)

        for i in range(1, 32):
            # 1->0,1, 2->0,3, 5->1,0, 6->1,2
            r = (i - 1) // 4
            c = 2 * ((i - 1) % 4) + (1 if r % 2 == 0 else 0)

            node = self._board[i]
            if node and node.piece:
                piece = node.piece
                if isinstance(piece, Queen):
                    match piece.color:
                        case Color.Red:
                            state[r, c, 0] = 1.0
                            state[r, c, 2] = 1.0
                        case Color.Black:
                            state[r, c, 1] = 1.0
                            state[r, c, 2] = 1.0
                else:
                    match piece.color:
                        case Color.Red:
                            state[r, c, 0] = 1.0
                        case Color.Black:
                            state[r, c, 1] = 1.0

        return state

    def is_game_over(self) -> bool:
        if self.red_pieces == 0:
            return True
        elif self.black_pieces == 0:
            return True

        if not self.get_legal_moves(self._turn):
            return True

        return False

    def get_winner(self):
        if self.red_pieces == 0:
            return Color.Black

        if self.black_pieces == 0:
            return Color.Red

        if not self.get_legal_moves(self._turn):
            return Color.Black if self._turn == Color.Red else Color.Black

        return None

    def get_legal_moves(self, player: Color) -> list[LegalMove]:
        # ToDo: bitboards https://3dkingdoms.com/checkers/bitboards.htm

        moves : dict[str, list] = defaultdict(list)

        # 2x11x18
        # 10-14

        piece_nodes = {
            i : n for i, n in self._board.items()
            if n.piece and n.piece.color == player
        }

        for square, node in piece_nodes.items():
            neighbors = node.get_neighbor_squares()
            #squares = [n.square for n in neighbors if n and not n.piece]

            def check_neighbors(neighbor_node):
                if not neighbor_node:
                    return
                if not neighbor_node.piece:
                    moves[square].append(neighbor[1].square)
                else:
                    if neighbor_node.piece.color != player:
                        pass

            for neighbor in neighbors:
                check_neighbors(neighbor)

            # if len(neighbors):
            #     left_neighbor = neighbors[0]
            #     right_neighbor = neighbors[1]
            #
            #     #capture squares
            #     if player == Color.Black:
            #         if left_neighbor:
            #             down_left_neighbor = left_neighbor.get_neighbors(Directions.DOWN_LEFT)
            #             if left_neighbor.piece and left_neighbor.piece.color == Color.Red and down_left_neighbor and down_left_neighbor.piece is None:
            #                 squares.append(down_left_neighbor.square)
            #
            #         if right_neighbor:
            #             down_right_neighbor = right_neighbor.get_neighbors(Directions.DOWN_RIGHT)
            #             if right_neighbor.piece and right_neighbor.piece.color == Color.Red and down_right_neighbor and down_right_neighbor.piece is None:
            #                 squares.append(down_right_neighbor.square)
            #
            #     elif player == Color.Red:
            #         if left_neighbor:
            #             up_left_neighbor = left_neighbor.get_neighbors(Directions.UP_LEFT)
            #             if left_neighbor.piece and left_neighbor.piece.color == Color.Black and up_left_neighbor and up_left_neighbor.piece is None:
            #                 squares.append(up_left_neighbor.square)
            #
            #         if right_neighbor:
            #             up_right_neighbor = right_neighbor.get_neighbors(Directions.UP_RIGHT)
            #             if right_neighbor.piece and right_neighbor.piece.color == Color.Black and up_right_neighbor and up_right_neighbor.piece is None:
            #                 squares.append(up_right_neighbor.square)
            #
            # if len(squares):
            #     moves[square] = squares

        return moves

board = Board()
board.move_piece(Move('9', '14'))
board.move_piece(Move('23', '18'))
board.display()
print(board.get_legal_moves(Color.Black))