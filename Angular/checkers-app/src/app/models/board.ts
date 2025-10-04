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
    private _gameId: string;
    private _started: boolean;
    private _event$: Subject<Move>;

    constructor(playerId: string, gameId: string, event$: Subject<Move>) {
        this._actionHistory = new Stack<Action>();
        this._playerId = playerId;
        this._gameId = gameId;
        this._event$ = event$;
        this._started = false;

        this.initialize();
    }

    public get playerId(): string {
        return this._playerId;
    }

    public get turn(): string {
        return this._turn === PieceColor.BLACK ? 'Black' : 'Red';
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

        game.history.forEach((move: HistoryEntry) => {
            let [from_square, to_square] = this.getMoveSquaresById(move.from_, move.to_);

            if (!from_square || !to_square) {
                console.error(`Invalid move: from ${move.from_} or to ${move.to_} not found on the board.`);
            } else {
                switch (move.event_type) {
                    case ActionType.MOVE:
                        this.move_piece(from_square, to_square, move.player_id);
                        this.recordAction(new Action(ActionType.MOVE, to_square.id, move.player_id));
                        break;
                    case ActionType.CAPTURE:
                        this.capture_piece(to_square, move.player_id);
                        this.recordAction(new Action(ActionType.CAPTURE, to_square.id, move.player_id));
                        break;
                    case ActionType.PROMOTE:
                        this.promote_piece(to_square, move.player_id);
                        this.recordAction(new Action(ActionType.PROMOTE, to_square.id, move.player_id));
                        break;
                }
            }
        });
    }

    public replay(pdn: string, captured: string[], player_id: string) {
        if (this._playerId !== player_id) {
            // apply the move
            let squares = Utils.parsePDN(pdn);
            let pairs = Utils.pairwise(squares);

            pairs.forEach(([from, to]) => {
                let [from_square, to_square] = this.getMoveSquaresById(from, to);
                
                if (!from_square || !to_square) {
                    console.error(`Invalid move: from ${from} or to ${to} not found on the board.`);
                } else {
                    this.move_piece(from_square, to_square, player_id);
                }
            });

            captured.forEach((cap) => {
                let cap_square = this.getSquareById(cap);
                if (cap_square) {
                    this.capture_piece(cap_square, player_id);
                } else {
                    console.error(`Invalid capture: square ${cap} not found on the board.`);
                }
            });

            let move = new Move(player_id);
            squares.forEach(sq => {
                move.addSquare(sq);
            });

            this._moveHistory.push(move);
        } else {
            // confirm the move is the same as the last move sent
        }
    }

    public click(square: Square) {
        let last_action = this._actionHistory.peek();
        let current_action : Action | null = null;

        switch (last_action?.type) {
            case ActionType.SELECT: {
                if (last_action.square === square.id) {
                    // if the last selected square is the same as the current square, unselect it
                    square.unselect();
                    current_action = new Action(ActionType.UNSELECT, square.id, this._playerId);

                    let moves = this.getAvailableMoves(square);
                    for (let [moveSquare, move] of moves) {
                        moveSquare.unselect();
                    }
                } else {
                    // record a move from the last selected square to the current different square
                    let [from_square, to_square] = this.getMoveSquaresById(last_action.square, square.id);

                    let moves = this.getAvailableMoves(from_square!);
                    let move = moves.get(to_square!);

                    if (!!move) {
                        if (move instanceof AvailableJump) {
                            this.capture_piece(move.captured?.square!, this._playerId);
                            current_action = new Action(ActionType.CAPTURE, square.id, this._playerId);
                            this._move?.addCapture(square.id, move.captured?.square.id!);
                        } else if (move instanceof AvailableMove) {
                            current_action = new Action(ActionType.MOVE, square.id, this._playerId);
                            this._move?.addSquare(square.id);
                        }

                        if (!!from_square) {
                            from_square.unselect();
                            
                            for (let [moveSquare, move] of moves) {
                                moveSquare.unselect();
                            }
                        }

                        this.move_piece(from_square!, to_square!, this._playerId);

                        if (this.checkPromotionAvailability(from_square!, to_square!)) {
                            this.promote_piece(to_square!, this._playerId);
                        }

                        if (move instanceof AvailableJump) {
                            moves = this.getAvailableMoves(to_square!);
                            const hasJump = Array.from(moves.values()).some(m => m instanceof AvailableJump);
                            if (!hasJump) {
                                this._event$.next(this._move!);
                                this._moveHistory.push(this._move!);
                                this._move = null;
                            }
                        } else if (move instanceof AvailableMove) {
                            this._event$.next(this._move!);
                            this._moveHistory.push(this._move!);
                            this._move = null;
                        }
                    }
                }
                break;
            }
            case ActionType.MOVE: {
                let [from_square, to_square] = this.getMoveSquaresById(last_action.square, square.id);

                from_square?.unselect();
                to_square?.unselect();

                this.switch_turn();

                square.select();
                current_action = new Action(ActionType.SELECT, square.id, this._playerId);

                if (this._move) {
                    this._event$.next(this._move!);
                    this._moveHistory.push(this._move!);
                    this._move = null;
                }
                
                this._move = new Move(this._playerId);
                this._move.addSquare(square.id);

                let moves = this.getAvailableMoves(square);
                for (let [moveSquare, move] of moves) {
                    moveSquare.select();
                }

                break;
            }
            case null:
            case undefined:
            case ActionType.UNSELECT:
                // if not last action, select the square
                square.select();
                current_action = new Action(ActionType.SELECT, square.id, this._playerId);

                if (this._move) {
                    this._event$.next(this._move!);
                    this._moveHistory.push(this._move!);
                    this._move = null;
                }

                this._move = new Move(this._playerId);
                this._move.addSquare(square.id);

                let moves = this.getAvailableMoves(square);
                for (let [moveSquare, move] of moves) {
                    moveSquare.select();
                }

                break;
            case ActionType.CAPTURE: {
                // if the last action was a capture, move a piece in chain and capture the piece
                let [from_square, to_square] = this.getMoveSquaresById(last_action.square, square.id);

                let moves = this.getAvailableMoves(from_square!);
                let move = moves.get(to_square!);

                if (!!move && move instanceof AvailableJump) {
                    this.capture_piece(move.captured?.square!, this._playerId);
                    current_action = new Action(ActionType.CAPTURE, square.id, this._playerId);
                    this.move_piece(from_square!, to_square!, this._playerId);

                    this._move?.addCapture(square.id, move.captured?.square.id!);
                    moves = this.getAvailableMoves(from_square!);
                    const hasJump = Array.from(moves.values()).some(m => m instanceof AvailableJump);
                    if (!hasJump) {
                        console.log("No more jumps available, switching turn");
                        this._event$.next(this._move!);
                        this._moveHistory.push(this._move!);
                        this._move = null;
                    }

                    if (this.checkPromotionAvailability(from_square!, to_square!)) {
                        this.promote_piece(to_square!, this._playerId);
                    }
                } else {
                    current_action = new Action(ActionType.SELECT, square.id, this._playerId);
                    let moves = this.getAvailableMoves(square);
                    for (let [moveSquare, move] of moves) {
                        moveSquare.select();
                    }

                    if (this._move) {
                        this._event$.next(this._move!);
                        this._moveHistory.push(this._move!);
                        this._move = null;
                    }

                    this._move = new Move(this._playerId);
                    this._move.addSquare(square.id);
                }
                
                break;
            }
            case ActionType.PROMOTE:
                current_action = new Action(ActionType.PROMOTE, square.id, this._playerId);
                break;
            default:
                console.error('Unknown action type:', last_action?.type);
                current_action = new Action(ActionType.UNSELECT, square.id, this._playerId);
                break;
        }

        this.recordAction(current_action!);
    }

    private getAvailableMoves(square: Square): Map<Square, AvailableMove> {
        let piece = this._pieces.get(square);
        let moves: Map<Square, AvailableMove> = new Map<Square, AvailableMove>();

        if (!piece) {
            console.warn(`No piece found on square ${square.id}`);
            return moves;
        }

        //let directions = [square.leftSibling, square.rightSibling];
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

    private checkPromotionAvailability(from: Square, to: Square) : boolean {
        let piece = this._pieces.get(to);

        if (!piece) {
            return false;
        }

        return piece.color === PieceColor.BLACK && ['29','30','31','32'].includes(to.id) ||
            piece.color === PieceColor.RED && ['1','2','3','4'].includes(to.id);
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
    }
}
