import { nanoid } from "nanoid";
import { BlackSquare, Square, WhiteSquare } from "./square";
import { Action, ActionType } from "./action";
import { Move } from "./move";
import { Piece, PieceColor, Queen } from "./piece";
import { Game } from "./game";
import { Direction } from "./direction";
import { AvailableMove, CapturedPiece } from "./available-move";

export class Board {
    private _board: Square[][] = [[]];  // 2D array of squares, where each square is represented by a Square object
    private _pieces: Map<Square, Piece> = new Map<Square, Piece>(); // Map of square ID to Piece object
    private playerId: string; // Player ID for the game
    private started: boolean;
    private selectedSquare: Square | null;
    private history: Move[] = [];
    private _turn: PieceColor = PieceColor.BLACK; // Black moves first

    constructor() {
        this._board = Array.from({ length: 8 }, () => new Array(8).fill(null));
        this.started = false;
        this.selectedSquare = null;
        this.playerId = nanoid();
        console.log(`Player ID: ${this.playerId}`);

        this.initialize();
    }

    public get turn(): string {
        return this._turn === PieceColor.BLACK ? 'Black' : 'Red';
    }

    public get board(): Square[][] {
        return this._board;
    }

    public get pieces(): Map<Square, Piece> {
        return this._pieces;
    }

    public load(game: Game) {
        this.started = true;

        game.history.forEach(entry => {
            this.reply(new Move(entry.from_, entry.to_, entry.player_id, new Piece(PieceColor.BLACK))); // Assuming all moves are black pieces for simplicity

            // ToDo: switch turn based on player_id
        });

        console.log('Current turn:', this._turn == PieceColor.BLACK ? 'Black' : 'Red');
    }

    public getHistory() {
        return [...this.history]; // returns a shallow copy
    }

    public reply(move: Move) {
        // Handle the reply for a move
        console.log(`Replying to move from ${move.from} to ${move.to} with piece ${move.piece?.color}`);

        if (move.playerId === this.playerId) {
            console.log(`Move from player ${move.playerId} matches current player ID ${this.playerId}`);
            return;
        }

        let from_square = this._board.flat().find(square => square.id === move.from);
        let to_square = this._board.flat().find(square => square.id === move.to);
        if (!from_square || !to_square) {
            console.error(`Invalid move: from ${move.from} or to ${move.to} not found on the board.`);
            return;
        }
        this.move_piece(from_square, to_square, null);
    }

    public click(square: Square) : Action {
        if (!this.started || !square.canSelect) {
            return new Action(ActionType.UNSELECT, square.id, this.playerId);
        }

        let piece = this._pieces.get(square);

        if (this.selectedSquare) {
            let selectedPiece = this._pieces.get(this.selectedSquare);

            // Unselect the square if it's already selected
            if (this.selectedSquare.id === square.id) {
                this.clearSelection(this.selectedSquare, piece);
                this.selectedSquare = null;

                return new Action(ActionType.UNSELECT, square.id, this.playerId);
            }

            // Select a different square with the same color piece
            if (piece && selectedPiece && piece.color === selectedPiece.color) {
                this.clearSelection(this.selectedSquare, piece);
                square.select();
                this.selectedSquare = square;

                return new Action(ActionType.SELECT, square.id, this.playerId);
            }

            // Attempt to move a piece
            const [from, to] = [this.selectedSquare, square];
            let availableMoves = this.getAvailableMoves(from, selectedPiece!);
            
            if (!availableMoves.has(to)) {
                console.error(`Invalid move from ${from.id} to ${to.id}`);

                this.clearSelection(this.selectedSquare, piece);
                this.selectedSquare = null;

                return new Action(ActionType.UNSELECT, square.id, this.playerId);
            }

            this.move_piece(this.selectedSquare, square, availableMoves.get(to)?.piece?.square || null);
            this.clearSelection(this.selectedSquare, piece);
            this.selectedSquare = null;

            // ToDo: while jumps are available, the player should be able to select the next jump

            return new Action(ActionType.MOVE, square.id, this.playerId);
        } else {
            // If no square is selected, select the clicked square
            if (!piece || piece.color !== this._turn) {
                console.error(`Cannot select square ${square.id} with piece color ${piece?.color}. It's ${this._turn} turn.`);
                return new Action(ActionType.UNSELECT, square.id, this.playerId);
            }

            square.select();
            this.selectedSquare = square;

            for (let move of this.getAvailableMoves(square, piece)) {
                move[0].select();
            }

            return new Action(ActionType.SELECT, square.id, this.playerId);
        }
    }

    private clearSelection(square: Square, piece: Piece | undefined): void {
        square.unselect();
        square.siblings.forEach(sibling => sibling.unselect());

        if (piece) {
            for (let move of this.getAvailableMoves(square, piece)) {
                move[0].unselect();
            }
        }
    }

    private getAvailableMoves(square: Square, piece: Piece): Map<Square, AvailableMove> {
        let moves: Map<Square, AvailableMove> = new Map<Square, AvailableMove>();
        let [left, right] = [square.leftSibling(piece.color), square.rightSibling(piece.color)];

        if (left) {
            if (!this._pieces.has(left)) {
                moves.set(left, new AvailableMove(square, left, undefined));
            } else if (this._pieces.get(left)?.color !== piece.color) {
                let jumpSquare = left.leftSibling(piece.color);
                if (jumpSquare && !this._pieces.has(jumpSquare)) {
                    moves.set(jumpSquare, new AvailableMove(square, jumpSquare, new CapturedPiece(left, this._pieces.get(left)!)));
                }
            }
        }

        if (right) {
            if (!this._pieces.has(right)) {
                moves.set(right, new AvailableMove(square, right, undefined));
            } else if (this._pieces.get(right)?.color !== piece.color) {
                let jumpSquare = right.rightSibling(piece.color);
                if (jumpSquare && !this._pieces.has(jumpSquare)) {
                    moves.set(jumpSquare, new AvailableMove(square, jumpSquare, new CapturedPiece(right, this._pieces.get(right)!)));
                }
            }
        }

        return moves;
    }

    private move_piece(from: Square, to: Square, captured: Square | null): void {
        let piece = this._pieces.get(from);

        if (!!piece) {
            this.history.push(new Move(from.id, to.id, this.playerId, piece));
            this.switchTurn();

            this._pieces.set(to, piece);
            this._pieces.delete(from); // Remove piece from the 'from' square

            if (captured) {
                this._pieces.delete(captured); // Remove captured piece from the board
            }
        }

        /*if (from.piece && to.color === 'dark' && !to.piece) {
            to.piece = from.piece;
            from.piece = null;

            // Check for promotion to queen
            if (to.position.startsWith('8') || to.position.startsWith('1')) {
                to.piece = new Piece(PieceColor.RED); // Assuming promotion to RED queen
            }
        }*/
    }

    private switchTurn(): void {
        this._turn = this._turn === PieceColor.BLACK ? PieceColor.RED : PieceColor.BLACK;
    }

    private initialize() {
        let blackId = 1;
        let whiteId = -1;

        for (let row = 0; row <= 7; row++) {
            this._board[row] = new Array(8).fill(0); // Initialize each row with 8 squares
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
                } else {
                    square = new WhiteSquare(whiteId.toString());
                    whiteId--;
                }

                this._board[row][col] = square;
            }
        }

        // Set siblings for each square
        for (let row = 0; row < 8; row++) {
            for (let col = 0; col < 8; col++) {
                const square = this._board[row][col];
                if (square instanceof BlackSquare) {
                    // Add siblings for dark squares
                    if (row > 0 && col > 0) square.addSibling(Direction.UP_LEFT, this._board[row - 1][col - 1]);
                    if (row > 0 && col < 7) square.addSibling(Direction.UP_RIGHT, this._board[row - 1][col + 1]);
                    if (row < 7 && col > 0) square.addSibling(Direction.DOWN_LEFT, this._board[row + 1][col - 1]);
                    if (row < 7 && col < 7) square.addSibling(Direction.DOWN_RIGHT, this._board[row + 1][col + 1]);
                }
            }
        }
    }
}