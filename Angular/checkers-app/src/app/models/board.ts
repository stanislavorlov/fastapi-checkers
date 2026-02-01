import { Subject } from "rxjs";
import { Action, ActionType } from "./action";
import { AvailableJump, AvailableMove, CapturedPiece } from "./available-move";
import { Direction } from "./direction";
import { Game, HistoryEntry } from "./game";
import { Move } from "./move";
import { Piece, Queen } from "./piece";
import { PieceColor } from "./piece-color";
import { BlackSquare, Square, WhiteSquare } from "./square";
import { Stack } from "./stack";
import { Utils } from "./utils";

export class Board {
    private _boardMatrix: Square[][] = [[]];  // 2D array of squares, where each square is represented by a Square object
    private _boardMap: Map<string, Square> = new Map<string, Square>(); // Map of square ID to Square object
    private _pieces: Map<Square, Piece> = new Map<Square, Piece>(); // Map of Square to Piece object
    private _actionHistory: Stack<Action>;
    private _moveHistory: Move[] = [];
    private _move: Move | null = null;
    private _turn: PieceColor = PieceColor.BLACK; // Black moves first
    private _playerId: string;
    private _playerColor?: PieceColor;
    private _started: boolean;
    private _finished: boolean = false;
    private _event$: Subject<Move>;
    private _forcedCapture: boolean = false;
    private _activeJumpingPiece: Square | null = null;

    constructor(playerId: string, event$: Subject<Move>) {
        this._actionHistory = new Stack<Action>();
        this._playerId = playerId;
        this._event$ = event$;
        this._started = false;

        this.initialize();
    }

    public get playerId(): string {
        return this._playerId;
    }

    public set playerId(playerId: string) {
        this._playerId = playerId;
    }

    public get turn(): string {
        return this._turn === PieceColor.BLACK ? 'Black' : 'Red';
    }

    public get finished(): boolean {
        return this._finished;
    }

    public set finished(value: boolean) {
        this._finished = value;
    }

    *[Symbol.iterator]() {
        if (this._playerColor == PieceColor.RED || !this._playerColor) {
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
        this._started = true;

        if (this._playerId === game.dark_player) {
            this._playerColor = PieceColor.BLACK;
        } else {
            this._playerColor = PieceColor.RED;
        }

        if (!!game.history) {
            game.history.sort((a, b) => a.sequence - b.sequence).forEach((entry: HistoryEntry) => {
                this.applyHistoryEntry(entry, game.dark_player);
            });
        }

        if (game.finished_at) {
            this._finished = true;
        }

        this.updateForcedCapture();
    }

    private applyHistoryEntry(entry: HistoryEntry, darkPlayerId: string) {
        const isCapture = entry.move.includes('x');
        const squares = Utils.parsePDN(entry.move);
        const pairs = Utils.pairwise(squares);

        const move = new Move(entry.player_id, entry.player_id == darkPlayerId ? PieceColor.BLACK : PieceColor.RED);
        move.addSquare(squares[0]);

        let captureIdx = 0;
        pairs.forEach(([from, to]) => {
            const [from_square, to_square] = this.getMoveSquaresById(from, to);

            if (from_square && to_square) {
                this.move_piece(from_square, to_square, entry.player_id);

                if (isCapture && entry.captures && entry.captures[captureIdx]) {
                    const capSquare = this.getSquareById(entry.captures[captureIdx]);
                    if (capSquare) {
                        this.capture_piece(capSquare, entry.player_id);
                        move.addCapture(to, capSquare.id);
                    }
                    captureIdx++;
                } else {
                    move.addSquare(to);
                }

                if (this.checkPromotionAvailability(from_square, to_square)) {
                    this.promote_piece(to_square, entry.player_id);
                }
            }
        });

        this._moveHistory.push(move);
        this.switch_turn();
        this.recordAction(new Action(isCapture ? ActionType.CAPTURE : ActionType.MOVE, squares[squares.length - 1], entry.player_id));
    }

    public reset() {
        this._pieces.clear();
        this._moveHistory = [];
        this._actionHistory = new Stack<Action>();
        this._turn = PieceColor.BLACK;
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
        if (!this._started || this._finished) return false;
        if (this._playerColor !== this._turn) return false;

        const last_action = this._actionHistory.peek();
        const piece = this._pieces.get(square);

        // 1. If in a multi-jump sequence, ONLY the active piece and its targets are clickable
        if (this._activeJumpingPiece) {
            if (this._activeJumpingPiece === square) return true;
            return this.getAvailableMoves(this._activeJumpingPiece).has(square);
        }

        // 2. Normal piece selection
        if (piece?.color === this._turn && this.getAvailableMoves(square).size > 0) {
            return true;
        }

        // 3. Target squares for selected piece
        if (last_action?.type === ActionType.SELECT) {
            if (last_action.square === square.id) return true; // Unselect

            const selectedSquare = this.getSquareById(last_action.square);
            if (selectedSquare && this.getAvailableMoves(selectedSquare).has(square)) {
                return true;
            }
        }

        return false;
    }

    public replay(pdn: string, captured: string[], player_id: string, player_color: PieceColor) {
        if (this._playerId !== player_id) {
            const isCapture = pdn.includes('x');
            const squares = Utils.parsePDN(pdn);
            const pairs = Utils.pairwise(squares);

            const move = new Move(player_id, player_color);
            move.addSquare(squares[0]);

            let captureIdx = 0;
            pairs.forEach(([from, to]) => {
                const [from_square, to_square] = this.getMoveSquaresById(from, to);

                if (from_square && to_square) {
                    this.move_piece(from_square, to_square, player_id);

                    if (isCapture && captured && captured[captureIdx]) {
                        const capSquare = this.getSquareById(captured[captureIdx]);
                        if (capSquare) {
                            this.capture_piece(capSquare, player_id);
                            move.addCapture(to, capSquare.id);
                        }
                        captureIdx++;
                    } else {
                        move.addSquare(to);
                    }

                    if (this.checkPromotionAvailability(from_square, to_square)) {
                        this.promote_piece(to_square, player_id);
                    }
                }
            });

            this._moveHistory.push(move);
            this.switch_turn();
            this.recordAction(new Action(isCapture ? ActionType.CAPTURE : ActionType.MOVE, squares[squares.length - 1], player_id));
        }
    }

    public click(square: Square) {
        if (!this._started || this._finished) return;

        let last_action = this._actionHistory.peek();
        let current_action: Action | null = null;

        const piece = this._pieces.get(square);
        const isPlayersPiece = piece?.color === this._turn;

        switch (last_action?.type) {
            case ActionType.SELECT:
            case ActionType.CAPTURE: {
                if (last_action.square === square.id) {
                    if (last_action.type === ActionType.SELECT) {
                        square.unselect();
                        current_action = new Action(ActionType.UNSELECT, square.id, this._playerId);
                        this._move = null;
                        this._activeJumpingPiece = null;
                        const moves = this.getAvailableMoves(square);
                        for (let [moveSquare, m] of moves) moveSquare.unselect();
                    }
                    break;
                }

                const from_square = this.getSquareById(last_action.square);
                if (!from_square) break;

                const moves = this.getAvailableMoves(from_square);
                const move = moves.get(square);

                if (move) {
                    if (move instanceof AvailableJump) {
                        this.capture_piece(move.captured?.square!, this._playerId);
                        current_action = new Action(ActionType.CAPTURE, square.id, this._playerId);
                        this._move?.addCapture(square.id, move.captured?.square.id!);
                    } else {
                        current_action = new Action(ActionType.MOVE, square.id, this._playerId);
                    }

                    this._move?.addSquare(square.id);

                    from_square.unselect();
                    for (let [ms, m] of moves) ms.unselect();

                    this.move_piece(from_square, square, this._playerId);

                    if (this.checkPromotionAvailability(from_square, square)) {
                        this.promote_piece(square, this._playerId);
                    }

                    if (move instanceof AvailableJump) {
                        const nextMoves = this.getAvailableMoves(square);
                        const hasJump = Array.from(nextMoves.values()).some(m => m instanceof AvailableJump);

                        if (hasJump) {
                            this._activeJumpingPiece = square;
                            square.select();
                            for (let [ns, m] of nextMoves) ns.select();
                        } else {
                            this.completeMove();
                        }
                    } else {
                        this.completeMove();
                    }
                } else if (!this._activeJumpingPiece && isPlayersPiece) {
                    // Switch selection
                    from_square.unselect();
                    for (let [ms, m] of moves) ms.unselect();

                    const newMoves = this.getAvailableMoves(square);
                    if (newMoves.size > 0) {
                        square.select();
                        current_action = new Action(ActionType.SELECT, square.id, this._playerId);
                        this._move = new Move(this._playerId, this._playerColor!);
                        this._move.addSquare(square.id);
                        for (let [ms, m] of newMoves) ms.select();
                    }
                }
                break;
            }
            default:
                if (isPlayersPiece) {
                    const moves = this.getAvailableMoves(square);
                    if (moves.size > 0) {
                        square.select();
                        current_action = new Action(ActionType.SELECT, square.id, this._playerId);
                        this._move = new Move(this._playerId, this._playerColor!);
                        this._move.addSquare(square.id);
                        for (let [ms, m] of moves) ms.select();
                    }
                }
                break;
        }

        if (current_action) {
            this.recordAction(current_action);
        }
    }

    private completeMove() {
        if (this._move) {
            this._event$.next(this._move);
            this._moveHistory.push(this._move);
            this._move = null;
        }
        this._activeJumpingPiece = null;
        this.switch_turn();
    }

    private getAvailableMoves(square: Square): Map<Square, AvailableMove> {
        let piece = this._pieces.get(square);
        if (!piece || piece.color !== this._turn) return new Map();

        const rawMoves = this.getRawAvailableMoves(square);

        if (this._forcedCapture) {
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
        this._forcedCapture = false;
        for (let [square, piece] of this._pieces) {
            if (piece.color === this._turn) {
                const rawMoves = this.getRawAvailableMoves(square);
                if (Array.from(rawMoves.values()).some(m => m instanceof AvailableJump)) {
                    this._forcedCapture = true;
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

    private checkPromotionAvailability(from: Square, to: Square): boolean {
        let piece = this._pieces.get(to);

        if (!piece) {
            return false;
        }

        return piece.color === PieceColor.BLACK && ['29', '30', '31', '32'].includes(to.id) ||
            piece.color === PieceColor.RED && ['1', '2', '3', '4'].includes(to.id);
    }

    private getSquareById(id: string): Square | undefined {
        return this._boardMap.get(id);
    }

    private getMoveSquaresById(fromId: string, toId: string): [Square | undefined, Square | undefined] {
        return [this.getSquareById(fromId), this.getSquareById(toId)];
    }

    private move_piece(from: Square, to: Square, player_id: string): void {
        this._pieces.set(to, this._pieces.get(from)!);
        this._pieces.delete(from);
    }

    private capture_piece(square: Square, player_id: string): void {
        this._pieces.delete(square);
    }

    private promote_piece(square: Square, player_id: string): void {
        if (this._pieces.has(square)) {
            let piece = this._pieces.get(square);
            this._pieces.set(square, new Queen(piece!.color));
        }
    }

    private recordAction(action: Action): void {
        this._actionHistory.push(action);
    }

    private switch_turn(): void {
        this._turn = this._turn === PieceColor.BLACK ? PieceColor.RED : PieceColor.BLACK;
        this.updateForcedCapture();
    }

    private initialize() {
        let blackId = 1;
        let whiteId = -1;

        for (let row = 0; row <= 7; row++) {
            this._boardMatrix[row] = new Array(8).fill(0); // Initialize each row with 8 squares
            for (let col = 0; col < 8; col++) {
                const isDark = (row + col) % 2 === 1;

                let piece: Piece | null = null;
                let square: Square | null = null;

                if (isDark) {
                    if (row <= 2) {
                        piece = new Piece(PieceColor.BLACK);
                    } else if (row >= 5) {
                        piece = new Piece(PieceColor.RED);
                    }

                    square = new BlackSquare(blackId.toString());
                    if (piece) {
                        this._pieces.set(square, piece);
                    }
                    blackId++;

                    this._boardMap.set(square.id, square);
                } else {
                    square = new WhiteSquare(whiteId.toString());
                    whiteId--;
                }

                this._boardMatrix[row][col] = square;
            }
        }

        // Set siblings for each square
        for (let row = 0; row < 8; row++) {
            for (let col = 0; col < 8; col++) {
                const square = this._boardMatrix[row][col];
                if (square instanceof BlackSquare) {
                    // Add siblings for dark squares
                    if (row > 0 && col > 0) square.addSibling(Direction.UP_LEFT, this._boardMatrix[row - 1][col - 1]);
                    if (row > 0 && col < 7) square.addSibling(Direction.UP_RIGHT, this._boardMatrix[row - 1][col + 1]);
                    if (row < 7 && col > 0) square.addSibling(Direction.DOWN_LEFT, this._boardMatrix[row + 1][col - 1]);
                    if (row < 7 && col < 7) square.addSibling(Direction.DOWN_RIGHT, this._boardMatrix[row + 1][col + 1]);
                }
            }
        }

        this.updateForcedCapture();
    }
}
