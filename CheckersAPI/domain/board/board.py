from itertools import pairwise
from typing import List, Tuple
from domain.board.bitboard import BitboardCheckers
from domain.board.board_history import BoardHistory
from domain.history_entry import HistoryEntry
from domain.king import King
from domain.man import Man
from domain.pdn_move import PdnMove
from domain.piece_factory import PieceFactory
from domain.side import Side
from domain.legal_move import LegalMove, CapturedMove

class Board:

    def __init__(self):
        super().__init__()
        self._turn = Side.Dark
        self._bitboard = BitboardCheckers()
        self._history = BoardHistory.empty()
        self._active_piece_sq = None # Square of piece that MUST continue jumping

        for sq in range(1, 13):  # white men
            self.set_piece(sq, Man(Side.Dark).acronym)
        for sq in range(21, 33):  # black men
            self.set_piece(sq, Man(Side.Light).acronym)

    @property
    def turn(self):
        return self._turn

    @property
    def bitboard(self):
        """Return a copy of the bitboard to prevent direct modification."""
        return self._bitboard.copy()

    @staticmethod
    def from_history(history: List[HistoryEntry]): # Accept List[HistoryEntry]
        board = Board()
        board._history = BoardHistory(history) # Store as BoardHistory
        
        # Replay history
        for item in history:
            board.apply_move(PdnMove(item.pdn_string, item.captures))

        return board

    def apply_move(self, pdn_move: PdnMove) -> bool:
        squares = pdn_move.move_squares

        if not squares:
            print(f'There are no squares in pdn_move: {pdn_move.as_string}')
            return False

        for prev, cur in pairwise(squares):
            legal_moves = self.get_legal_moves(self._turn)

            legal_move = next((m for m in legal_moves if m.from_ == prev and m.to_ == cur), None)

            if not legal_move:
                print(f"There is no legal move from {prev} to {cur} found in the board (Turn: {self._turn})")
                return False

            self.move_piece(legal_move)

        return True

    def switch_turn(self):
        self._turn = Side.Dark if self._turn == Side.Light else Side.Light

    def get_piece(self, square: int) -> str | None:
        """Return the piece acronym at a square (1-32)."""
        return self._bitboard.piece_at(square)

    def set_piece(self, square: int, acronym: str):
        """Place a piece on the board."""
        self._bitboard.set_piece(square, acronym)

    def remove_piece(self, square: int):
        """Remove any piece from square."""
        self._bitboard.remove_piece(square)

    def get_occupancy(self, color: str) -> int:
        """Return bitboard of occupied squares for color."""
        return self._bitboard.occupancy_of(color)

    def generate_moves(self, color: str):
        """Generate all legal non-capturing moves for given color."""
        return self._bitboard.generate_moves(color)

    def generate_captures(self, color: str):
        """Generate all legal capturing moves for given color."""
        return self._bitboard.generate_captures(color)

    def display(self):
        """Pretty print board in 8x8 format."""
        mapping = {None: "."}
        for sq in range(1, 33):
            piece_bit = self.get_piece(sq)
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

    def display_squares(self):
        """Print all 32 squares and their piece values."""
        lines = []
        for sq in range(1, 33):
            piece_bit = self.get_piece(sq)
            piece = PieceFactory.get_piece(piece_bit)
            val = piece.acronym if piece else "EMPTY"
            lines.append(f"Square {sq:2}: {val}")
        
        print("\n--- Board Square State ---")
        for i in range(0, 32, 4):
            print(" | ".join(lines[i:i+4]))
        print("--------------------------\n")

    def copy(self):
        new_board = Board()
        new_board._turn = self._turn
        new_board._active_piece_sq = self._active_piece_sq
        new_board._history = BoardHistory(self._history.items[:])
        new_board._bitboard = self.bitboard # Use property which returns a copy

        return new_board

    def is_game_over(self) -> bool:

        match self._turn:
            case Side.Dark:
                if self.get_occupancy("black") == 0:
                    return True
            case Side.Light:
                if self.get_occupancy("white") == 0:
                    return True

        if not self.get_legal_moves(self._turn):
            return True

        return False

    def get_winner(self):
        if self.get_occupancy("black") == 0:
            return Side.Light

        if self.get_occupancy("white") == 0:
            return Side.Dark

        if not self.get_legal_moves(self._turn):
            return Side.Dark if self._turn == Side.Light else Side.Light

        return None

    def move_piece(self, legal_move: LegalMove):
        """
        Apply a single legal move (one segment) to the board.
        Used by MCTS and apply_move.
        """
        from_sq = legal_move.from_
        to_sq = legal_move.to_
        
        piece_bit = self.get_piece(from_sq)
        piece = PieceFactory.get_piece(piece_bit)
        
        if not piece:
            return False

        is_capture = isinstance(legal_move, CapturedMove)

        # 1. Remove from source
        self.remove_piece(from_sq)
        
        # 2. Handle capture
        if isinstance(legal_move, CapturedMove):
            self.remove_piece(legal_move.jumped)
            
        # 3. Handle promotion
        is_promoted = False
        if piece.color == Side.Dark and piece.is_man and 29 <= to_sq <= 32:
            piece = King(piece.color)
            is_promoted = True
        elif piece.color == Side.Light and piece.is_man and 1 <= to_sq <= 4:
            piece = King(piece.color)
            is_promoted = True
            
        # 4. Set at destination
        self.set_piece(to_sq, piece.acronym)
        
        # 5. Turn switching and Multi-jump logic
        can_continue_jump = False
        if is_capture and not is_promoted:
            # Check for further captures from the destination square with the same piece
            color_str = "black" if piece.color == Side.Dark else "white"
            all_captures = self._bitboard.generate_captures(color_str)
            if any(c[0] == to_sq for c in all_captures):
                can_continue_jump = True
        
        if can_continue_jump:
            self._active_piece_sq = to_sq
            # Turn does NOT switch
        else:
            self._active_piece_sq = None
            self.switch_turn()
            
        return True

    def get_legal_moves(self, player: Side) -> list[LegalMove]:
        legal_moves : List[LegalMove] = []
        color = "black" if player == Side.Dark else "white"

        # 1. Multi-jump logic: if a piece is in the middle of jumping, it MUST continue
        if self._active_piece_sq:
            captures = self.generate_captures(color)
            for capture in captures:
                if capture[0] == self._active_piece_sq:
                    legal_moves.append(CapturedMove(capture[0], capture[1], capture[2]))
            return legal_moves

        # 2. Mandatory captures: if any capture is possible, only captures are legal
        captures = self.generate_captures(color)
        if captures:
            for capture in captures:
                legal_moves.append(CapturedMove(capture[0], capture[1], capture[2]))
            return legal_moves

        # 3. Normal moves
        moves = self.generate_moves(color)
        for move in moves:
            legal_moves.append(LegalMove(move[0], move[1]))

        return legal_moves