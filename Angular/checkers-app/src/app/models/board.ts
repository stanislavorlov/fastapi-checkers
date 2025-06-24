import { Square } from "../square";
import { Piece, PieceColor } from "./piece";

export class Board {
    // The standard 8x8 board has 32 squares used for play, numbered 1-32. 
    // Black pieces start on squares 1 to 12
    // White pieces start on squares 21 to 32

    private _board: Map<number, Square[]>;
    private started: boolean;

    constructor() {
        this._board = new Map<number, Square[]>();
        this.started = false;

        this.initialize();
    }

    public getView() {
        return Array.from(this._board.entries());
    }

    public load() {
        this.started = true;
    }

    public click(square: Square) : void {
        if (this.started) {
            
        }
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