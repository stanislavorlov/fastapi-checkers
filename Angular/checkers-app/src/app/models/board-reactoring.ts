import { nanoid } from "nanoid";
import { Action, ActionType } from "./action";
import { AvailableJump, AvailableMove, CapturedPiece } from "./available-move";
import { Direction } from "./direction";
import { Game, HistoryEntry } from "./game";
import { Move } from "./move";
import { Piece, PieceColor } from "./piece";
import { BlackSquare, Square, WhiteSquare } from "./square";
import { Stack } from "./stack";

export class Board2 {

    private _boardMatrix: Square[][] = [[]];  // 2D array of squares, where each square is represented by a Square object
    private _boardMap: Map<string, Square> = new Map<string, Square>(); // Map of square ID to Square object
    private _pieces: Map<Square, Piece> = new Map<Square, Piece>(); // Map of Square to Piece object
    private _history: Stack<Action>;
    private _turn: PieceColor = PieceColor.BLACK; // Black moves first
    private _playerId: string;

    constructor() {
        this._history = new Stack<Action>();
        this._playerId = nanoid();
        console.log(`Player ID: ${this._playerId}`);

        this.initialize();
    }

    public get turn(): string {
        return this._turn === PieceColor.BLACK ? 'Black' : 'Red';
    }

    public get board(): Square[][] {
        return this._boardMatrix;
    }

    public get pieces(): Map<Square, Piece> {
        return this._pieces;
    }

    public getHistory() {
        return [...this._history]; // returns a shallow copy
    }

    public reply(move: Move): void {

    }

    public load(game: Game) {
        game.history = [];
        game.history.push({ player_id: '', event_type: ActionType.MOVE, from_: '10', to_: '14' }); // Initial empty move
        game.history.push({ player_id: '', event_type: ActionType.MOVE, from_: '22', to_: '18' });
        game.history.push({ player_id: '', event_type: ActionType.MOVE, from_: '11', to_: '16' });
        game.history.push({ player_id: '', event_type: ActionType.MOVE, from_: '24', to_: '20' });
        game.history.push({ player_id: '', event_type: ActionType.MOVE, from_: '7', to_: '10' });
        game.history.push({ player_id: '', event_type: ActionType.MOVE, from_: '21', to_: '17' });
        game.history.push({ player_id: '', event_type: ActionType.MOVE, from_: '2', to_: '7' });
        game.history.push({ player_id: '', event_type: ActionType.MOVE, from_: '27', to_: '24' });
        game.history.push({ player_id: '', event_type: ActionType.MOVE, from_: '10', to_: '15' });

        game.history.forEach((move: HistoryEntry) => {
            let [from_square, to_square] = this.getMoveSquaresById(move.from_, move.to_);

            if (!from_square || !to_square) {
                console.error(`Invalid move: from ${move.from_} or to ${move.to_} not found on the board.`);
            } else {
                switch (move.event_type) {
                    case ActionType.MOVE:
                        this.move_piece(from_square, to_square, move.player_id);
                        break;
                    case ActionType.CAPTURE:
                        this.capture_piece(to_square, move.player_id);
                        break;
                    case ActionType.PROMOTE:
                        this.promote_piece(from_square, to_square, move.player_id);
                        break;
                }
            }
        });
    }

    //select
    //move
    //select
    //move
    //select
    //move
    //capture
    //select
    //move
    //capture

    public click(square: Square): Action {
        let last_action = this._history.peek();
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

                    if (moves.has(to_square!)) {
                        let move = moves.get(to_square!);
                        
                        if (move instanceof AvailableJump) {
                            this.capture_piece(move.captured?.square!, this._playerId);
                            current_action = new Action(ActionType.CAPTURE, square.id, this._playerId);

                        } else if (move instanceof AvailableMove) {
                            current_action = new Action(ActionType.MOVE, square.id, this._playerId);

                            // Unselect both the destination and origin squares
                            square.unselect();
                            from_square?.unselect();
                        }

                        this.move_piece(from_square!, to_square!, this._playerId);
                    }
                }
                break;
            }
            case ActionType.MOVE: {
                let [from_square, to_square] = this.getMoveSquaresById(last_action.square, square.id);

                from_square?.unselect();
                to_square?.unselect();

                this.switch_turn();
                break;
            }
            case null:
            case undefined:
            case ActionType.UNSELECT:
                // if not last action, select the square
                square.select();
                current_action = new Action(ActionType.SELECT, square.id, this._playerId);

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
                } else {
                    current_action = new Action(ActionType.UNSELECT, square.id, this._playerId);
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

        return current_action!;
    }

    private getAvailableMoves(square: Square): Map<Square, AvailableMove> {
        let piece = this._pieces.get(square);
        let moves: Map<Square, AvailableMove> = new Map<Square, AvailableMove>();

        if (!piece) {
            console.warn(`No piece found on square ${square.id}`);
            return moves;
        }

        let [left, right] = [square.leftSibling(piece.color), square.rightSibling(piece.color)];

        if (!!left) {
            let move = this.checkSiblingsAvailablity(piece, square, left, (color) => square.leftSibling(color)?.leftSibling(color));
            if (move) {
                moves.set(move.to, move);
            }
        }
        if (!!right) {
            let move = this.checkSiblingsAvailablity(piece, square, right, (color) => square.rightSibling(color)?.rightSibling(color));
            if (move) {
                moves.set(move.to, move);
            }
        }

        return moves;
    }

    private checkSiblingsAvailablity(piece: Piece, square: Square, sibling: Square, get_sibling: (color: PieceColor) => Square | undefined): AvailableMove {
        if (!this._pieces.has(sibling)) {
            return new AvailableMove(square, sibling);
        } else if (this._pieces.get(sibling)?.color !== piece.color) {
            let jumpSquare = get_sibling(piece.color);
            if (jumpSquare && !this._pieces.has(jumpSquare)) {
                return new AvailableJump(square, jumpSquare, new CapturedPiece(sibling, this._pieces.get(sibling)!));
            }
        }

        return null as any;
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

    private promote_piece(from: Square, to: Square, player_id: string): void {
        
    }

    private recordAction(action: Action): void {
        this._history.push(action);
    }

    private switch_turn(): void {
        // Logic to switch the turn between players
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
