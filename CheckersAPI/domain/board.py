from typing import List, Optional
from domain.king import King
from domain.man import Man
from domain.piece import Piece
from domain.piece_factory import PieceFactory
from domain.side import Side
from domain.kernel.domain_event import PieceMovedEvent, PieceCapturedEvent, TurnSwitchedEvent
from domain.kernel.entity import Entity
from domain.legal_move import LegalMove, CapturedMove

class Board(Entity):

    def __init__(self):
        super().__init__()

        self._turn = Side.Dark
        self.MOVE_MAP, self.CAPTURE_MAP = self._generate_maps()

        # bitboards (integers) for different piece types
        self.bitboards : dict[str, int] = {}
        pieces = [Man(Side.Dark), Man(Side.Light), King(Side.Dark), King(Side.Light)]

        for piece in pieces:
            self.bitboards[piece.acronym] = 0

        for sq in range(1, 13):  # white men
            self.set_piece(sq, Man(Side.Dark))
        for sq in range(21, 33):  # black men
            self.set_piece(sq, Man(Side.Light))

    @property
    def turn(self):
        return self._turn

    @staticmethod
    def bit(square: int) -> int:
        """Return bit mask for square (1–32)."""
        return 1 << square

    def set_piece(self, square: int, piece: Piece):
        """Place a piece on the board."""
        mask = self.bit(square)
        self.bitboards[piece.acronym] |= mask

    def remove_piece(self, square: int):
        """Remove any piece from square."""
        mask = ~self.bit(square)

        for bitboard in self.bitboards:
            self.bitboards[bitboard] &= ~mask

    def piece_at(self, square: int) -> Piece | None:
        """Return the piece at a square."""
        mask = self.bit(square)

        for key, bitboard in self.bitboards.items():
            if bitboard & mask:
                return PieceFactory.get_piece(key)

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

        if piece.color != self._turn:
            return

        legal_moves = self.get_legal_moves(self._turn)

        direction = 1 if self._turn == Side.Dark else -1
        condition = lambda m: m.from_ == from_square and (m.from_ - m.to_) * direction < 0
        legal_move = next((m for m in legal_moves if condition(m)), None)

        self.remove_piece(from_square)

        if isinstance(legal_move, CapturedMove):
            print(f'Captured move, removing piece at {legal_move.jumped}')
            self.remove_piece(legal_move.jumped)

            self.raise_event(PieceCapturedEvent(captured_at=legal_move.jumped))

        # detect promotions
        promotion = False
        if piece.color == Side.Dark and piece.is_man and 29 <= to_square <= 32:
            piece = King(piece.color)
            promotion = True
        elif piece.color == Side.Light and piece.is_man and 1 <= to_square <= 4:
            piece = King(piece.color)
            promotion = True

        self.set_piece(to_square, piece)

        super().raise_event(PieceMovedEvent(moved_from=from_square, moved_to=to_square))

        if promotion:
            self.switch_turn()

            super().raise_event(TurnSwitchedEvent(current_turn=self._turn))
        else:
            legal_moves = self.get_legal_moves(self._turn)

            filtered = [m for m in legal_moves if condition(m)]

            # if no legal moves for the current piece (no future capturing), update the turn
            if all(not isinstance(m, CapturedMove) for m in filtered):
                self.switch_turn()

                super().raise_event(TurnSwitchedEvent(current_turn=self._turn))

    def switch_turn(self):
        self._turn = Side.Dark if self._turn == Side.Light else Side.Light

    def occupancy(self) -> int:
        """Return bitboard of all occupied squares."""
        return self.bitboards[Side.Dark.value.lower()] | self.bitboards[Side.Dark.value] | self.bitboards[Side.Light.value.lower()] | self.bitboards[Side.Light.value]

    def display(self):
        """Pretty print board in 8x8 format."""
        mapping = {None: "."}
        for sq in range(1, 33):
            piece = self.piece_at(sq)
            if piece:
                mapping[sq] = '⚫' if (piece.color == Side.Dark) else '🔴'
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
        new_board.bitboards = self.bitboards

        return new_board

    def is_game_over(self) -> bool:

        match self._turn:
            case Side.Dark:
                if self.bitboards[Side.Dark.value.lower()] == 0 and self.bitboards[Side.Dark.value] == 0:
                    return True
            case Side.Light:
                if self.bitboards[Side.Light.value.lower()] == 0 and self.bitboards[Side.Light.value] == 0:
                    return True

        if not self.get_legal_moves(self._turn):
            return True

        return False

    def get_winner(self):
        if self.bitboards[Side.Dark.value.lower()] == 0 and self.bitboards[Side.Dark.value] == 0:
            return Side.Light

        if self.bitboards[Side.Light.value.lower()] == 0 and self.bitboards[Side.Light.value] == 0:
            return Side.Dark

        if not self.get_legal_moves(self._turn):
            return Side.Dark if self._turn == Side.Light else Side.Dark

        return None

    def get_legal_moves(self, player: Side) -> list[LegalMove]:
        # Generate all legal non-capturing moves for given color.
        moves : List[LegalMove] = []
        if player == Side.Dark:
            men, kings = self.bitboards[Side.Dark.value.lower()], self.bitboards[Side.Dark.value]
            forward_dirs = [(-1, -1), (-1, 1)]  # downwards
        else:
            men, kings = self.bitboards[Side.Light.value.lower()], self.bitboards[Side.Light.value]
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
        if player == Side.Dark:
            men, kings = self.bitboards[Side.Dark.value.lower()], self.bitboards[Side.Dark.value]
            my_pieces = men | kings
            opp_pieces = self.bitboards[Side.Light.value.lower()] | self.bitboards[Side.Light.value]
        else:
            men, kings = self.bitboards[Side.Light.value.lower()], self.bitboards[Side.Light.value]
            my_pieces = men | kings
            opp_pieces = self.bitboards[Side.Dark.value.lower()] | self.bitboards[Side.Dark.value]

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
#board.move_piece(10, 14)
#board.move_piece(23, 19)
#board.display()
print(board.get_legal_moves(Side.Dark))