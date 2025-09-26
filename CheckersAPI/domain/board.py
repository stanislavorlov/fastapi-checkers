from typing import List
from domain.bitboard import BitboardCheckers
from domain.king import King
from domain.man import Man
from domain.piece_factory import PieceFactory
from domain.side import Side
from domain.kernel.domain_event import PieceMovedEvent, PieceCapturedEvent, TurnSwitchedEvent
from domain.kernel.entity import Entity
from domain.legal_move import LegalMove, CapturedMove

class Board(Entity):

    def __init__(self):
        super().__init__()
        self._turn = Side.Dark
        self._bitboard = BitboardCheckers()

        for sq in range(1, 13):  # white men
            self._bitboard.set_piece(sq, Man(Side.Dark).acronym)
        for sq in range(21, 33):  # black men
            self._bitboard.set_piece(sq, Man(Side.Light).acronym)

    @property
    def turn(self):
        return self._turn

    def move_piece(self, from_square: int, to_square: int):
        """
        Moves a piece on the board from one square to another.
        If captures is performed, it calculates the captured square and removes the piece.

        Args:
            from_square (int): The starting square index of the piece
            to_square (int): The target square index where the piece should move
        """
        piece_bit = self._bitboard.piece_at(from_square)
        piece = PieceFactory.get_piece(piece_bit)

        if not piece:
            print(f"Piece at {from_square} not found in the board")

            return

        if piece.color != self._turn:
            print(f"It is not {self._turn}'s turn")

            return

        legal_moves = self.get_legal_moves(self._turn)
        legal_move = next((m for m in legal_moves if m.from_ == from_square and m.to_ == to_square), None)

        self._bitboard.remove_piece(from_square)

        was_captured_move = False
        if isinstance(legal_move, CapturedMove):
            print(f'Captured move, removing piece at {legal_move.jumped}')
            self._bitboard.remove_piece(legal_move.jumped)

            was_captured_move = True

            self.raise_event(PieceCapturedEvent(captured_at=legal_move.jumped))

        # detect promotions
        promotion = False
        if piece.color == Side.Dark and piece.is_man and 29 <= to_square <= 32:
            piece = King(piece.color)
            promotion = True
        elif piece.color == Side.Light and piece.is_man and 1 <= to_square <= 4:
            piece = King(piece.color)
            promotion = True

        self._bitboard.set_piece(to_square, piece.acronym)

        super().raise_event(PieceMovedEvent(moved_from=from_square, moved_to=to_square))

        if promotion:
            self.switch_turn()

            super().raise_event(TurnSwitchedEvent(current_turn=self._turn))
        else:
            if not was_captured_move:
                self.switch_turn()

                super().raise_event(TurnSwitchedEvent(current_turn=self._turn))
            else:
                legal_moves = self.get_legal_moves(self._turn)
                filtered = [m for m in legal_moves if m.from_ == to_square]

                # if no legal moves for the current piece (no future capturing), update the turn
                if all(not isinstance(m, CapturedMove) for m in filtered):
                    self.switch_turn()

                    super().raise_event(TurnSwitchedEvent(current_turn=self._turn))

    def switch_turn(self):
        self._turn = Side.Dark if self._turn == Side.Light else Side.Light

    def display(self):
        """Pretty print board in 8x8 format."""
        mapping = {None: "."}
        for sq in range(1, 33):
            piece_bit = self._bitboard.piece_at(sq)
            piece = PieceFactory.get_piece(piece_bit)
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
        new_board._bitboard = self._bitboard

        return new_board

    def is_game_over(self) -> bool:

        match self._turn:
            case Side.Dark:
                if self._bitboard.occupancy_of("black") == 0:
                    return True
            case Side.Light:
                if self._bitboard.occupancy_of("white") == 0:
                    return True

        if not self.get_legal_moves(self._turn):
            return True

        return False

    def get_winner(self):
        if self._bitboard.occupancy_of("black") == 0:
            return Side.Light

        if self._bitboard.occupancy_of("white") == 0:
            return Side.Dark

        if not self.get_legal_moves(self._turn):
            return Side.Dark if self._turn == Side.Light else Side.Dark

        return None

    def get_legal_moves(self, player: Side) -> list[LegalMove]:
        legal_moves : List[LegalMove] = []
        color = "black" if self._turn == Side.Dark else "white"

        moves = self._bitboard.generate_moves(color)
        for move in moves:
            legal_moves.append(LegalMove(move[0], move[1]))

        captures = self._bitboard.generate_captures(color)
        for capture in captures:
            legal_moves.append(CapturedMove(capture[0], capture[1], capture[2]))

        return legal_moves