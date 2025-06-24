import { Square } from "./square";

export class Board {
    // The standard 8x8 board has 32 squares used for play, numbered 1-32. 
    // Black pieces start on squares 1 to 12
    // White pieces start on squares 21 to 32

    private _board: Map<number, Square[]>;

    constructor() {
        this._board = new Map<number, Square[]>();
        this.initialize();
    }

    public getView() {
        return Array.from(this._board.entries());
    }

    public load() {

    }

    private initialize() {
        let positionCounter = 1;

        for (let row = 1; row <= 8; row++) {
            const cells: Square[] = [];

            for (let col = 0; col < 8; col++) {
                const isDark = (row + col) % 2 === 1;
                const color: 'light' | 'dark' = isDark ? 'dark' : 'light';

                let piece: string = '';
                if (isDark) {
                    if (row <= 3) {
                        piece = 'black_piece';
                    } else if (row >= 6) {
                        piece = 'red_piece';
                    }
                }

                const position = isDark ? positionCounter.toString() : '';
                if (isDark) positionCounter++;

                cells.push(new Square(position, color, piece ));
            }

            this._board.set(row, cells);
        }
    }
}