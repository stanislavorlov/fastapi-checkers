import { nanoid } from "nanoid";
import { BlackSquare, Square, WhiteSquare } from "./square";
import { Action, ActionType } from "./action";
import { Move } from "./move";
import { Piece, PieceColor, Queen } from "./piece";
import { Game } from "./game";

export class Board {
    // The standard 8x8 board has 32 squares used for play, numbered 1-32. 
    // Black pieces start on squares 1 to 12
    // White pieces start on squares 21 to 32

    private playerId: string; // Player ID for the game
    private _board: Map<string, [Square, Piece | null]>; // Map of square ID to Square object
    private started: boolean;
    private selectedSquare: Square | null;
    private history: Move[] = [];
    private turn: PieceColor = PieceColor.BLACK; // Black moves first

    // create additional data structures 2d array with the reference to the squares

    constructor() {
        this._board = new Map<string, [Square, Piece | null]>();
        this.started = false;
        this.selectedSquare = null;
        this.playerId = nanoid();
        console.log(`Player ID: ${this.playerId}`);

        this.initialize();
    }

    public getView() {
        const result: Map<string, [Square, Piece | null][]> = new Map<string, [Square, Piece | null][]>();
        const boardMap = this._board;
        
        for (let row = 1; row <= 8; row++) {
            const cells: [Square, Piece | null][] = [];
            for (let col = 1; col <= 8; col++) {
                const isDark = (row + col) % 2 === 1;
                let key = ((row - 1) * 4 + Math.floor((col - 1) / 2) + 1).toString();
                if (!isDark) {
                    key = (-key).toString(); // Negative for white squares
                }
                const square = boardMap.get(key);
                if (square) {
                    cells.push(square);
                }
            }
            result.set(row.toString(), cells);
        }

        return Array.from(result.entries());
    }

    public load(game: Game) {
        this.started = true;

        game.history.forEach(entry => {
            //this.reply(new Move(entry.from_, entry.to_, entry.player_id, new Piece()));

            // ToDo: switch turn based on player_id
        });
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

        let from: [Square, Piece | null] | undefined = this._board.get(move.from);
        let to: [Square, Piece | null] | undefined = this._board.get(move.to);

        if (from && to) {
            console.log(`Moving piece from ${from[0].id} to ${to[0].id}`);

            from[1] = null; // Remove piece from the 'from' square
            to[1] = move.piece; // Place piece on the 'to' square

            this.switchTurn();
        } else {
            console.error(`Invalid move: from ${move.from} or to ${move.to} not found on the board.`);
        }
    }

    public click(square: Square) : Action {
        if (this.started && square.canSelect) {
            if (!!this.selectedSquare) {
                const [from, to] = [this.selectedSquare, square];
                if (!this.canMove(from, to)) {
                    console.error(`Invalid move from ${from.id} to ${to.id}`);

                    this.selectedSquare.unselect();
                    square.unselect();

                    return new Action(ActionType.UNSELECT, square.id, this.playerId);
                }
                this.move_piece(this.selectedSquare, square);

                this.selectedSquare.unselect();
                this.selectedSquare = null;

                return new Action(ActionType.MOVE, square.id, this.playerId);
            } else {
                square.select();
                this.selectedSquare = square;

                return new Action(ActionType.SELECT, square.id, this.playerId);
            }
        }

        return new Action(ActionType.UNSELECT, square.id, this.playerId);
    }

    private canMove(from: Square, to: Square): boolean {
        /*if (this.turn !== from.piece?.color) {
            console.error(`It's not ${from.piece?.color} turn.`);
            return false;
        }

        // Check if the destination square is empty and is a dark square
        if (from.piece && !to.piece && to.color === 'dark') {
            // Check if the move is diagonal and within one square
            return from.piece.canMove(Number(from.position), Number(to.position));
        }*/
        return false;
    }

    private move_piece(from: Square, to: Square): void {
        /*this.history.push(new Move(from.position, to.position, this.playerId, from.piece));
        this.switchTurn();

        to.switchPiece(from.piece);
        from.switchPiece(null);*/

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

        for (let row = 1; row <= 8; row++) {
            for (let col = 0; col < 8; col++) {
                const isDark = (row + col) % 2 === 1;

                let piece: Piece | null = null;
                if (isDark) {
                    if (row <= 3) {
                        piece = new Piece(PieceColor.BLACK);
                    } else if (row >= 6) {
                        piece = new Piece(PieceColor.RED);
                    }
                }

                if (isDark) {
                    this._board.set(blackId.toString(), [new BlackSquare(blackId.toString()), piece]);
                    blackId++;
                } else {
                    this._board.set(whiteId.toString(), [new WhiteSquare(whiteId.toString()), null]);
                    whiteId--;
                }
            }
        }
    }
}