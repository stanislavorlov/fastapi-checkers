import { Square } from "../square";
import { Action, ActionType } from "./action";
import { Move } from "./move";
import { Piece, PieceColor, Queen } from "./piece";

export class Board {
    // The standard 8x8 board has 32 squares used for play, numbered 1-32. 
    // Black pieces start on squares 1 to 12
    // White pieces start on squares 21 to 32

    private _board: Map<number, Square[]>;
    private started: boolean;
    private selectedSquare: Square | null;
    private history: Move[] = [];
    private turn: PieceColor = PieceColor.BLACK; // Black moves first

    constructor() {
        this._board = new Map<number, Square[]>();
        this.started = false;
        this.selectedSquare = null;

        this.initialize();
    }

    public getView() {
        return Array.from(this._board.entries());
    }

    public load() {
        this.started = true;
    }

    public getHistory() {
        return [...this.history]; // returns a shallow copy
    }

    public click(square: Square) : Action {
        if (this.started) {
            if (!!this.selectedSquare) {
                // move piece only by black squares
                if (!!square.position) {
                    this.move_piece(this.selectedSquare, square);
                }

                this.selectedSquare.unselect();
                this.selectedSquare = null;

                return new Action(ActionType.MOVE, square.position, square.piece);
            } else {
                square.select();
                this.selectedSquare = square;

                return new Action(ActionType.SELECT, square.position, square.piece);
            }
        }
        
        return new Action(ActionType.UNSELECT, square.position, null);
    }

    private canMove(from: Square, to: Square): boolean {
        let isMan = from.piece && from.piece instanceof Piece;
        let isQueen = from.piece && from.piece instanceof Queen;
        
        if (this.turn !== from.piece?.color) {
            console.error(`It's not ${from.piece?.color} turn.`);
            return false;
        }

        // Check if the destination square is empty and is a dark square
        if (from.piece && !to.piece && to.color === 'dark') {
            // Check if the move is diagonal and within one square
            if (isMan) {
                return from.piece.canMove(Number(from.position), Number(to.position));
            } else {

            }
            
            return false;
        }
        return false;
    }

    private move_piece(from: Square, to: Square): void {
        if (!this.canMove(from, to)) {
            console.error(`Invalid move from ${from.position} to ${to.position}`);
            return;
        }

        this.history.push(new Move(from.position, to.position, from.piece));
        this.switchTurn();

        to.switchPiece(from.piece);
        from.switchPiece(null);

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
        let positionCounter = 1;

        for (let row = 1; row <= 8; row++) {
            const cells: Square[] = [];

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

                const position = isDark ? positionCounter.toString() : '';
                if (isDark) positionCounter++;

                cells.push(new Square(position, isDark ? 'dark' : 'light', piece ));
            }

            this._board.set(row, cells);
        }
    }
}