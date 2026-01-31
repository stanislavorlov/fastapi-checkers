class BitboardCheckers:
    def __init__(self):
        # bitboards (integers) for different piece types
        self.black_men   = 0
        self.black_kings = 0
        self.white_men   = 0
        self.white_kings = 0
        self.MOVE_MAP, self.CAPTURE_MAP = self._generate_maps()

    @staticmethod
    def bit(square: int) -> int:
        """Return bit mask for square (1–32)."""
        return 1 << (square - 1)

    def copy(self):
        """Return a copy of the bitboard."""
        copy_bitboard = BitboardCheckers()

        copy_bitboard.black_men = self.black_men
        copy_bitboard.black_kings = self.black_kings
        copy_bitboard.white_men = self.white_men
        copy_bitboard.white_kings = self.white_kings

        return copy_bitboard

    def set_piece(self, square: int, piece: str):
        """Place a piece on the board."""
        mask = self.bit(square)
        if piece == "b":
            self.black_men |= mask
        elif piece == "B":
            self.black_kings |= mask
        elif piece == "r":
            self.white_men |= mask
        elif piece == "R":
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
        if self.white_men & mask: return "r"
        if self.white_kings & mask: return "R"
        return None

    def move_piece(self, from_square: int, to_square: int, piece: str):
        self.remove_piece(from_square)
        self.set_piece(to_square, piece)

    def occupancy(self) -> int:
        """Return bitboard of all occupied squares."""
        return self.black_men | self.black_kings | self.white_men | self.white_kings

    def occupancy_of(self, color: str) -> int:
        match color:
            case "black":
                return self.black_men | self.black_kings
            case "white":
                return self.white_men | self.white_kings
            case _:
                return 0

    def print_board(self):
        """Pretty print board in 8x8 format."""
        mapping = {None: "."}
        for sq in range(1, 33):
            piece = self.piece_at(sq)
            mapping[sq] = piece if piece else "."

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

    def generate_moves(self, color: str):
        """Generate all legal non-capturing moves for given color: black or white."""
        moves = []
        if color == "black":
            men, kings = self.black_men, self.black_kings
            forward_dirs = [(1, -1), (1, 1)]  # downwards
        else:
            men, kings = self.white_men, self.white_kings
            forward_dirs = [(-1, -1), (-1, 1)]  # upwards

        occ = self.occupancy()
        # Generate moves for men
        for sq in range(1, 33):
            if not (men & self.bit(sq)): continue
            for neigh, direction in self.MOVE_MAP[sq]:
                if direction in forward_dirs:
                    if not (occ & self.bit(neigh)):
                        moves.append((sq, neigh))
        # Generate moves for kings (both directions)
        for sq in range(1, 33):
            if not (kings & self.bit(sq)): continue
            for neigh, _ in self.MOVE_MAP[sq]:
                if not (occ & self.bit(neigh)):
                    moves.append((sq, neigh))
        return moves

    def generate_captures(self, color: str):
        """Generate all legal capturing moves for given color: black or white."""
        captures = []
        if color == "black":
            men, kings = self.black_men, self.black_kings
            opp_pieces = self.white_men | self.white_kings
            forward_dirs = [(1, -1), (1, 1)]  # downwards
        else:
            men, kings = self.white_men, self.white_kings
            opp_pieces = self.black_men | self.black_kings
            forward_dirs = [(-1, -1), (-1, 1)]  # upwards

        occ = self.occupancy()
        # Captures for men (only forward)
        for sq in range(1, 33):
            if not (men & self.bit(sq)): continue
            for jumped, land, direction in self.CAPTURE_MAP[sq]:
                if direction in forward_dirs:
                    if (opp_pieces & self.bit(jumped)) and not (occ & self.bit(land)):
                        captures.append((sq, land, jumped))
        # Captures for kings (all directions)
        for sq in range(1, 33):
            if not (kings & self.bit(sq)): continue
            for jumped, land, _ in self.CAPTURE_MAP[sq]:
                if (opp_pieces & self.bit(jumped)) and not (occ & self.bit(land)):
                    captures.append((sq, land, jumped))
        return captures

    @staticmethod
    def _generate_maps():
        """Generate MOVE_MAP and CAPTURE_MAP automatically for 32 squares."""
        move_map, capture_map = {}, {}
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
                move_map[square] = []
                capture_map[square] = []
                for dr, dc in directions:
                    nr, nc = row + dr, col + dc
                    if 0 <= nr < 8 and 0 <= nc < 8 and board[nr][nc] != 0:
                        move_map[square].append((board[nr][nc], (dr, dc)))
                    jr, jc = row + 2 * dr, col + 2 * dc
                    if (0 <= jr < 8 and 0 <= jc < 8
                            and board[nr][nc] != 0 and board[jr][jc] != 0):
                        capture_map[square].append((board[nr][nc], board[jr][jc], (dr, dc)))
        return move_map, capture_map