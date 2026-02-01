import { Subject } from "rxjs";
import { AvailableJump, AvailableMove, CapturedPiece } from "./available-move";
import { Direction } from "./direction";
import { Game, HistoryEntry } from "./game";
import { Move } from "./move";
import { Piece, Queen } from "./piece";
import { PieceColor } from "./piece-color";
import { BlackSquare, Square, WhiteSquare } from "./square";
import { Utils } from "./utils";
import { BoardState } from "./board-state";

export class Board {
    private _boardMatrix: Square[][] = [[]];  // 2D array of squares, where each square is represented by a Square object
    private _boardMap: Map<string, Square> = new Map<string, Square>(); // Map of square ID to Square object
    private _pieces: Map<Square, Piece> = new Map<Square, Piece>(); // Map of Square to Piece object
    private _moveHistory: Move[] = [];
    private _move: Move | null = null;
    private _playerId: string;
    private _event$: Subject<Move>;
    private _state: BoardState;

    constructor(playerId: string, event$: Subject<Move>) {
        this._playerId = playerId;
        this._event$ = event$;
        this._state = new BoardState();

        this.initialize();
    }

    public get playerId(): string {
        return this._playerId;
    }

    public set playerId(playerId: string) {
        this._playerId = playerId;
    }

    public get turn(): string {
        return this._state.turn === PieceColor.BLACK ? 'Black' : 'Red';
    }

    public get finished(): boolean {
        return this._state.finished;
    }

    public set finished(value: boolean) {
        this._state.finished = value;
    }

    *[Symbol.iterator]() {
        if (this._state.playerColor == PieceColor.RED || !this._state.playerColor) {
            for (let row = 0; row < 8; row++) {
                yield { row, squares: this._boardMatrix[row] };
            }
        } else {
            for (let row = 7; row >= 0; row--) {
                yield { row, squares: this._boardMatrix[row] };
            }
        }
    }

    public get pieces(): Map<Square, Piece> {
        return this._pieces;
    }

    public getHistory() {
        return [...this._moveHistory]; // returns a shallow copy
    }

    public load(game: Game) {
        this._state.started = true;

        if (this._playerId === game.dark_player) {
            this._state.playerColor = PieceColor.BLACK;
        } else {
            this._state.playerColor = PieceColor.RED;
        }

        if (!!game.history) {
            game.history.sort((a, b) => a.sequence - b.sequence).forEach((entry: HistoryEntry) => {
                this.applyHistoryEntry(entry, game.dark_player);
            });
        }

        if (game.finished_at) {
            this._state.finished = true;
        }

        this.updateForcedCapture();
    }

    private applyHistoryEntry(entry: HistoryEntry, darkPlayerId: string) {
        this.applyPDNMove(
            entry.move,
            entry.captures || [],
            entry.player_id,
            entry.player_id === darkPlayerId ? PieceColor.BLACK : PieceColor.RED
        );
    }

    private applyPDNMove(pdn: string, captures: string[], playerId: string, playerColor: PieceColor) {
        const isCapture = pdn.includes('x');
        const squares = Utils.parsePDN(pdn);
        const pairs = Utils.pairwise(squares);

        const move = new Move(playerId, playerColor);
        move.addSquare(squares[0]);

        let captureIdx = 0;
        pairs.forEach(([from, to]) => {
            const [fromSquare, toSquare] = this.getMoveSquaresById(from, to);

            if (fromSquare && toSquare) {
                this.movePiece(fromSquare, toSquare, playerId);

                if (isCapture && captures && captures[captureIdx]) {
                    const capSquare = this.getSquareById(captures[captureIdx]);
                    if (capSquare) {
                        this.capturePiece(capSquare, playerId);
                        move.addCapture(to, capSquare.id);
                    }
                    captureIdx++;
                } else {
                    move.addSquare(to);
                }

                if (this.checkPromotionAvailability(toSquare)) {
                    this.promotePiece(toSquare, playerId);
                }
            }
        });

        this._moveHistory.push(move);
        this._state.switchTurn();
        this.updateForcedCapture();
    }

    public reset() {
        this._pieces.clear();
        this._moveHistory = [];
        this._state.reset();
        this.initialize();
    }

    public showMove(index: number, game: Game) {
        this.reset();
        const moves = [...game.history].sort((a, b) => a.sequence - b.sequence);
        for (let i = 0; i <= index; i++) {
            this.applyHistoryEntry(moves[i], game.dark_player);
        }
    }


    public isSquareClickable(square: Square): boolean {
        if (!this._state.canInteract()) return false;

        // If in a multi-jump sequence
        if (this._state.activeJumpingPiece) {
            return this._state.activeJumpingPiece === square ||
                this.getAvailableMoves(this._state.activeJumpingPiece).has(square);
        }

        const piece = this._pieces.get(square);
        const selectedSquare = this._state.selectedSquare;

        // Target squares for current selection
        if (selectedSquare) {
            if (selectedSquare === square) return true; // For unselecting
            if (this.getAvailableMoves(selectedSquare).has(square)) return true;
        }

        // Potential new piece selection
        if (piece?.color === this._state.turn && this.getAvailableMoves(square).size > 0) {
            return true;
        }

        return false;
    }

    public replay(pdn: string, captured: string[], player_id: string, player_color: PieceColor) {
        if (this._playerId !== player_id) {
            this.applyPDNMove(pdn, captured, player_id, player_color);
        }
    }

    public click(square: Square) {
        if (!this._state.canInteract()) return;

        const piece = this._pieces.get(square);
        const isPlayersPiece = piece?.color === this._state.turn;
        const selectedSquare = this._state.selectedSquare;
        const activeJumpingPiece = this._state.activeJumpingPiece;

        // 1. Handle Active Jumping Piece (Multi-jump)
        if (activeJumpingPiece) {
            if (activeJumpingPiece === square) {
                this.handleUnselect(square);
            } else {
                this.handleMoveAttempt(activeJumpingPiece, square);
            }
            return;
        }

        // 2. Handle Selected Piece
        if (selectedSquare) {
            if (selectedSquare === square) {
                this.handleUnselect(square);
            } else {
                const moves = this.getAvailableMoves(selectedSquare);
                if (moves.has(square)) {
                    this.handleMoveAttempt(selectedSquare, square);
                } else if (isPlayersPiece) {
                    this.handleSwitchSelection(selectedSquare, square);
                }
            }
            return;
        }

        // 3. Handle Initial Selection
        if (isPlayersPiece) {
            this.handleSelect(square);
        }
    }

    private handleSelect(square: Square) {
        const moves = this.getAvailableMoves(square);
        if (moves.size > 0) {
            this._state.select(square);
            this._move = new Move(this._playerId, this._state.playerColor!);
            this._move.addSquare(square.id);
            for (let [ms, m] of moves) ms.select();
        }
    }

    private handleUnselect(square: Square) {
        const moves = this.getAvailableMoves(square);
        for (let [ms, m] of moves) ms.unselect();
        this._state.unselect();
        this._move = null;
    }

    private handleSwitchSelection(from: Square, to: Square) {
        // Deselect old
        from.unselect();
        const oldMoves = this.getAvailableMoves(from);
        for (let [ms, m] of oldMoves) ms.unselect();

        // Select new
        this.handleSelect(to);
    }

    private handleMoveAttempt(from: Square, to: Square) {
        const moves = this.getAvailableMoves(from);
        const move = moves.get(to);

        if (!move) return;

        if (move instanceof AvailableJump) {
            this.capturePiece(move.captured?.square!, this._playerId);
            this._move?.addCapture(to.id, move.captured?.square.id!);
        }

        this._move?.addSquare(to.id);

        from.unselect();
        for (let [ms, m] of moves) ms.unselect();

        this.movePiece(from, to, this._playerId);

        if (this.checkPromotionAvailability(to)) {
            this.promotePiece(to, this._playerId);
        }

        if (move instanceof AvailableJump) {
            const nextMoves = this.getAvailableMoves(to);
            const hasMoreJumps = Array.from(nextMoves.values()).some(m => m instanceof AvailableJump);

            if (hasMoreJumps) {
                this._state.setActiveJumpingPiece(to);
                for (let [ns, m] of nextMoves) ns.select();
            } else {
                this.completeMove();
            }
        } else {
            this.completeMove();
        }
    }

    private completeMove() {
        if (this._move) {
            this._event$.next(this._move);
            this._moveHistory.push(this._move);
            this._move = null;
        }
        this._state.switchTurn();
        this.updateForcedCapture();
    }

    private getAvailableMoves(square: Square): Map<Square, AvailableMove> {
        let piece = this._pieces.get(square);
        if (!piece || piece.color !== this._state.turn) return new Map();

        const rawMoves = this.getRawAvailableMoves(square);

        if (this._state.forcedCapture) {
            const jumpsOnly = new Map<Square, AvailableMove>();
            for (let [target, move] of rawMoves) {
                if (move instanceof AvailableJump) {
                    jumpsOnly.set(target, move);
                }
            }
            return jumpsOnly;
        }

        return rawMoves;
    }

    private getRawAvailableMoves(square: Square): Map<Square, AvailableMove> {
        let piece = this._pieces.get(square);
        let moves: Map<Square, AvailableMove> = new Map<Square, AvailableMove>();

        if (!piece) {
            return moves;
        }

        let directions = square.siblings(piece.moveDirections);
        for (let [direction, sibling] of directions) {
            let jumpSquare = sibling.sibling(direction);

            let move = this.checkSiblingsAvailablity(piece, square, sibling, jumpSquare);
            if (move) {
                moves.set(move.to, move);
            }
        }

        return moves;
    }

    private updateForcedCapture() {
        this._state.forcedCapture = false;
        for (let [square, piece] of this._pieces) {
            if (piece.color === this._state.turn) {
                const rawMoves = this.getRawAvailableMoves(square);
                if (Array.from(rawMoves.values()).some(m => m instanceof AvailableJump)) {
                    this._state.forcedCapture = true;
                    return;
                }
            }
        }
    }

    private checkSiblingsAvailablity(piece: Piece, square: Square, sibling: Square, jumpSquare: Square | undefined): AvailableMove {
        if (!this._pieces.has(sibling)) {
            return new AvailableMove(square, sibling);
        } else if (this._pieces.get(sibling)?.color !== piece.color) {
            if (jumpSquare && !this._pieces.has(jumpSquare)) {
                return new AvailableJump(square, jumpSquare, new CapturedPiece(sibling, this._pieces.get(sibling)!));
            }
        }

        return null as any;
    }

    private checkPromotionAvailability(to: Square): boolean {
        const piece = this._pieces.get(to);
        if (!piece || piece instanceof Queen) return false;

        let row = -1;
        for (let r = 0; r < 8; r++) {
            if (this._boardMatrix[r].includes(to)) {
                row = r;
                break;
            }
        }

        return (piece.color === PieceColor.BLACK && row === 7) ||
            (piece.color === PieceColor.RED && row === 0);
    }

    private getSquareById(id: string): Square | undefined {
        return this._boardMap.get(id);
    }

    private getMoveSquaresById(fromId: string, toId: string): [Square | undefined, Square | undefined] {
        return [this.getSquareById(fromId), this.getSquareById(toId)];
    }

    private movePiece(from: Square, to: Square, player_id: string): void {
        this._pieces.set(to, this._pieces.get(from)!);
        this._pieces.delete(from);
    }

    private capturePiece(square: Square, player_id: string): void {
        this._pieces.delete(square);
    }

    private promotePiece(square: Square, player_id: string): void {
        const piece = this._pieces.get(square);
        if (piece) {
            this._pieces.set(square, new Queen(piece.color));
        }
    }

    private initialize() {
        this.initializeMatrix();
        this.initializeSiblings();
        this.updateForcedCapture();
    }

    private initializeMatrix() {
        let blackId = 1;
        let whiteId = -1;

        for (let row = 0; row <= 7; row++) {
            this._boardMatrix[row] = new Array(8);
            for (let col = 0; col < 8; col++) {
                const isDark = (row + col) % 2 === 1;
                let square: Square;

                if (isDark) {
                    square = new BlackSquare(blackId.toString());
                    this.placeInitialPiece(square, row);
                    this._boardMap.set(square.id, square);
                    blackId++;
                } else {
                    square = new WhiteSquare(whiteId.toString());
                    whiteId--;
                }
                this._boardMatrix[row][col] = square;
            }
        }
    }

    private placeInitialPiece(square: Square, row: number) {
        let piece: Piece | null = null;
        if (row <= 2) {
            piece = new Piece(PieceColor.BLACK);
        } else if (row >= 5) {
            piece = new Piece(PieceColor.RED);
        }

        if (piece) {
            this._pieces.set(square, piece);
        }
    }

    private initializeSiblings() {
        for (let row = 0; row < 8; row++) {
            for (let col = 0; col < 8; col++) {
                const square = this._boardMatrix[row][col];
                if (square instanceof BlackSquare) {
                    if (row > 0 && col > 0) square.addSibling(Direction.UP_LEFT, this._boardMatrix[row - 1][col - 1]);
                    if (row > 0 && col < 7) square.addSibling(Direction.UP_RIGHT, this._boardMatrix[row - 1][col + 1]);
                    if (row < 7 && col > 0) square.addSibling(Direction.DOWN_LEFT, this._boardMatrix[row + 1][col - 1]);
                    if (row < 7 && col < 7) square.addSibling(Direction.DOWN_RIGHT, this._boardMatrix[row + 1][col + 1]);
                }
            }
        }
    }
}
