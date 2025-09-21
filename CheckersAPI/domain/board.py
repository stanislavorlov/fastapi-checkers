from typing import List
from application.board_helper import BoardHelper
from domain.color import Color
from domain.legal_move import LegalMove, CapturedMove

class Board:

    def __init__(self):
        self._turn = Color.Black
        # bitboards (integers) for different piece types
        self.black_men = 0
        self.black_kings = 0
        self.white_men = 0
        self.white_kings = 0
        self.MOVE_MAP, self.CAPTURE_MAP = self._generate_maps()

        for sq in range(1, 13):  # white men
            self.set_piece(sq, "b")
        for sq in range(21, 33):  # black men
            self.set_piece(sq, "w")

    @property
    def turn(self):
        return self._turn

    @staticmethod
    def bit(square: int) -> int:
        """Return bit mask for square (1–32)."""
        return 1 << (square - 1)

    def set_piece(self, square: int, piece: str):
        """Place a piece on the board."""
        mask = self.bit(square)
        if piece == "b":
            self.black_men |= mask
        elif piece == "B":
            self.black_kings |= mask
        elif piece == "w":
            self.white_men |= mask
        elif piece == "W":
            self.white_kings |= mask

    def remove_piece(self, square: int):
        """Remove any piece from square."""
        mask = ~self.bit(square)
        self.black_men   &= mask
        self.black_kings &= mask
        self.white_men   &= mask
        self.white_kings &= mask

    def piece_at(self, square: int) -> str | None:
        """Return the piece at a square."""
        mask = self.bit(square)
        if self.black_men & mask: return "b"
        if self.black_kings & mask: return "B"
        if self.white_men & mask: return "w"
        if self.white_kings & mask: return "W"

        return None

    def move_piece(self, from_square: int, to_square: int):
        """
        Moves a piece on the board from one square to another.
        If captures is performed, it calculates the captured square and removes the piece.

        Args:
            from_square (int): The starting square index of the piece
            to_square (int): The target square index where the piece should move
        """
        piece = self.piece_at(from_square)

        if not piece:
            return

        legal_moves = self.get_legal_moves(self._turn)

        legal_move = next((m for m in legal_moves if m.from_ == from_square and (m.from_ < m.to_ if self._turn == Color.Black else m.from_ > m.to_)), None)

        self.remove_piece(from_square)

        if isinstance(legal_move, CapturedMove):
            print(f'captured piece: {legal_move.jumped}')
            self.remove_piece(legal_move.jumped)

        player = Color.Black if piece == "b" or piece == "B" else Color.Red

        # detect promotions
        promotion = False
        if piece == "b" and 29 <= to_square <= 32:
            piece = "B"
            promotion = True
        elif piece == "w" and 1 <= to_square <= 4:
            piece = "W"
            promotion = True

        self.set_piece(to_square, piece)

        if promotion:
            print('switching turn')
            self.switch_turn()
        else:
            legal_moves = self.get_legal_moves(player)

            filtered = [m for m in legal_moves if m.from_ == to_square and (m.to_ < m.from_ if self._turn == Color.Black else m.to_ > m.from_)]

            print(filtered)

            # if no legal moves for the current piece (no future capturing), update the turn
            if all(not isinstance(m, CapturedMove) for m in filtered):
                print('switching turn')
                self.switch_turn()

    def switch_turn(self):
        self._turn = Color.Black if self._turn == Color.Red else Color.Red

    def occupancy(self) -> int:
        """Return bitboard of all occupied squares."""
        return self.black_men | self.black_kings | self.white_men | self.white_kings

    def display(self):
        """Pretty print board in 8x8 format."""
        mapping = {None: "."}
        for sq in range(1, 33):
            piece = self.piece_at(sq)
            if piece:
                mapping[sq] = '⚫' if (piece == 'b' or piece == 'B') else '🔴'
            else:
                mapping[sq] = "."

        board = []
        idx = 1
        for row in range(8, 0, -1):
            line = []
            for col in range(0, 8):
                if (row + col) % 2 == 0:  # light square
                    line.append(" ")
                else:
                    line.append(mapping[idx])
                    idx += 1
            board.append(" ".join(line))
        print("\n".join(board))

    def copy(self):
        new_board = Board()
        new_board._turn = self._turn
        new_board.black_men = self.black_men
        new_board.black_kings = self.black_kings
        new_board.white_men = self.white_men
        new_board.white_kings = self.white_kings

        return new_board

    def is_game_over(self) -> bool:

        match self._turn:
            case Color.Black:
                if self.black_men == 0 and self.black_kings == 0:
                    return True
            case Color.Red:
                if self.white_men == 0 and self.white_kings == 0:
                    return True

        if not self.get_legal_moves(self._turn):
            return True

        return False

    def get_winner(self):
        if self.black_men == 0 and self.black_kings == 0:
            return Color.Red

        if self.white_men == 0 and self.white_kings == 0:
            return Color.Black

        if not self.get_legal_moves(self._turn):
            return Color.Black if self._turn == Color.Red else Color.Black

        return None

    def get_legal_moves(self, player: Color) -> list[LegalMove]:
        # Generate all legal non-capturing moves for given color.
        moves : List[LegalMove] = []
        if player == Color.Black:
            men, kings = self.black_men, self.black_kings
            forward_dirs = [(-1, -1), (-1, 1)]  # downwards
        else:
            men, kings = self.white_men, self.white_kings
            forward_dirs = [(1, -1), (1, 1)]  # upwards

        occ = self.occupancy()
        # Generate moves for men
        for sq in range(1, 33):
            if not (men & self.bit(sq)): continue
            for neigh, _ in self.MOVE_MAP[sq]:
                if not (occ & self.bit(neigh)):
                    moves.append(LegalMove(sq, neigh))
        # Generate moves for kings (both directions)
        for sq in range(1, 33):
            if not (kings & self.bit(sq)): continue
            for neigh, _ in self.MOVE_MAP[sq]:
                if not (occ & self.bit(neigh)):
                    moves.append(LegalMove(sq, neigh))

        # Generate all legal capturing moves for given color.
        if player == Color.Black:
            men, kings = self.black_men, self.black_kings
            my_pieces = men | kings
            opp_pieces = self.white_men | self.white_kings
        else:
            men, kings = self.white_men, self.white_kings
            my_pieces = men | kings
            opp_pieces = self.black_men | self.black_kings

        occ = self.occupancy()
        for sq in range(1, 33):
            if not (my_pieces & self.bit(sq)): continue
            for neigh, land in self.CAPTURE_MAP[sq]:
                if (opp_pieces & self.bit(neigh)) and not (occ & self.bit(land)):
                    moves.append(CapturedMove(sq, land, neigh))  # (from, to, jumped)

        return moves

    def _generate_maps(self):
        """Generate MOVE_MAP and CAPTURE_MAP automatically for 32 squares."""
        MOVE_MAP, CAPTURE_MAP = {}, {}
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
                MOVE_MAP[square] = []
                CAPTURE_MAP[square] = []
                for dr, dc in directions:
                    nr, nc = row + dr, col + dc
                    if 0 <= nr < 8 and 0 <= nc < 8 and board[nr][nc] != 0:
                        MOVE_MAP[square].append((board[nr][nc], None))
                    jr, jc = row + 2 * dr, col + 2 * dc
                    if (0 <= jr < 8 and 0 <= jc < 8
                            and board[nr][nc] != 0 and board[jr][jc] != 0):
                        CAPTURE_MAP[square].append((board[nr][nc], board[jr][jc]))

        return MOVE_MAP, CAPTURE_MAP

board = Board()
board.move_piece(10, 14)
board.move_piece(23, 19)
board.display()
print(board.get_legal_moves(Color.Black))