import { nanoid } from "nanoid";
import { BlackSquare, Square, WhiteSquare } from "./square";
import { Action, ActionType } from "./action";
import { Move } from "./move";
import { Piece, PieceColor, Queen } from "./piece";
import { Game } from "./game";

export class Board {
    private _board: Square[][] = [[]];  // 2D array of squares, where each square is represented by a Square object
    private _pieces: Map<Square, Piece> = new Map<Square, Piece>(); // Map of square ID to Piece object
    private playerId: string; // Player ID for the game
    private started: boolean;
    private selectedSquare: Square | null;
    private history: Move[] = [];
    private turn: PieceColor = PieceColor.BLACK; // Black moves first

    constructor() {
        this._board = Array.from({ length: 8 }, () => new Array(8).fill(null));
        this.started = false;
        this.selectedSquare = null;
        this.playerId = nanoid();
        console.log(`Player ID: ${this.playerId}`);

        this.initialize();
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

        console.log('Current turn:', this.turn == PieceColor.BLACK ? 'Black' : 'Red');
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
        this.move_piece(from_square, to_square);
    }

    public click(square: Square) : Action {
        //this._pieces.get(square)

        if (this.started && square.canSelect) {
            if (!!this.selectedSquare) {
                let piece = this._pieces.get(square);
                let selectedPiece = this._pieces.get(this.selectedSquare);

                // If a square is already selected, check if the clicked square is the same
                if (this.selectedSquare.id === square.id) {
                    // Unselect the square if it's already selected
                    this.selectedSquare.unselect();
                    this.getAvailableMoves(this.selectedSquare, piece).forEach(sibling => sibling.unselect());
                    this.selectedSquare = null;

                    return new Action(ActionType.UNSELECT, square.id, this.playerId);

                } else if (piece && selectedPiece && piece.color === selectedPiece.color) {
                    // If a square is selected with the same color piece
                    this.selectedSquare.unselect();
                    this.getAvailableMoves(this.selectedSquare, piece).forEach(sibling => sibling.unselect());
                    square.select();
                    this.selectedSquare = square;

                    return new Action(ActionType.SELECT, square.id, this.playerId);
                }

                const [from, to] = [this.selectedSquare, square];
                if (!this.canMove(from, to)) {
                    console.error(`Invalid move from ${from.id} to ${to.id}`);

                    this.selectedSquare.unselect();
                    square.unselect();
                    this.getAvailableMoves(this.selectedSquare, piece).forEach(sibling => sibling.unselect());
                    this.selectedSquare = null;

                    return new Action(ActionType.UNSELECT, square.id, this.playerId);
                }
                this.move_piece(this.selectedSquare, square);

                this.selectedSquare.unselect();
                square.unselect();
                this.getAvailableMoves(this.selectedSquare, piece).forEach(sibling => sibling.unselect());
                this.selectedSquare = null;

                return new Action(ActionType.MOVE, square.id, this.playerId);
            } else {
                let piece = this._pieces.get(square);

                if (!piece || piece.color !== this.turn) {
                    console.error(`Cannot select square ${square.id} with piece color ${piece?.color}. It's ${this.turn} turn.`);
                    return new Action(ActionType.UNSELECT, square.id, this.playerId);
                }

                square.select();
                this.selectedSquare = square;

                this.getAvailableMoves(square, piece).forEach(sibling => sibling.select());

                return new Action(ActionType.SELECT, square.id, this.playerId);
            }
        }

        return new Action(ActionType.UNSELECT, square.id, this.playerId);
    }

    private canMove(from: Square, to: Square): boolean {
        let piece = this._pieces.get(from);
        
        if (!!piece) {
            if (this.turn !== piece.color) {
                console.error(`It's not ${piece.color} turn.`);
                return false;
            }

            // Check if the destination square is empty and is a dark square
            if (to.color === 'dark' && !this._pieces.has(to)) {
                // Check if the move is diagonal and within one square
                if (piece.canMove(Number(from.id), Number(to.id))) {
                    return true;
                } else {
                    console.error(`Invalid move from ${from.id} to ${to.id}`);
                    return false;
                }
            }
        }

        return false;
    }

    private getAvailableMoves(square: Square, piece: Piece | undefined): Square[] {
        if (!piece) return [];

        if (piece.color === PieceColor.RED) {
            // For RED pieces, they can only move forward (to lower row numbers)
            return square.siblings.filter(sibling => !this._pieces.has(sibling) && Number(sibling.id) < Number(square.id));
        }
        // For BLACK pieces, they can move backward (to higher row numbers)
        return square.siblings.filter(sibling => !this._pieces.has(sibling) && Number(sibling.id) > Number(square.id));
    }

    private move_piece(from: Square, to: Square): void {
        let piece = this._pieces.get(from);

        if (!!piece) {
            this.history.push(new Move(from.id, to.id, this.playerId, piece));
            this.switchTurn();

            this._pieces.set(to, piece);
            this._pieces.delete(from); // Remove piece from the 'from' square
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
        this.turn = this.turn === PieceColor.BLACK ? PieceColor.RED : PieceColor.BLACK;
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
                    if (row > 0 && col > 0) square.addSibling(this._board[row - 1][col - 1]);
                    if (row > 0 && col < 7) square.addSibling(this._board[row - 1][col + 1]);
                    if (row < 7 && col > 0) square.addSibling(this._board[row + 1][col - 1]);
                    if (row < 7 && col < 7) square.addSibling(this._board[row + 1][col + 1]);
                }
            }
        }
    }
}