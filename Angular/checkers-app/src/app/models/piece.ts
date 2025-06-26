export enum PieceColor {
    BLACK = 1,
    RED = 2
}

export class Piece {
    private _color: PieceColor;

    constructor(color: PieceColor) {
        this._color = color;
    }

    get image() {
        return this._color == PieceColor.BLACK ? 'black_piece' : 'red_piece';
    }

    get isRed() {
        return this._color === PieceColor.RED;
    }

    get color() {
        return this._color;
    }

    canMove(from: number, to: number) : boolean {
        let diff = Number(from) - Number(to);

        if (this.isRed) {
            return diff == 3 || diff == 4 || diff == 5;
        } else {
            return diff == -3 || diff == -4 || diff == -5;
        }
    }
}

export class Queen extends Piece {
    constructor(color: PieceColor) {
        super(color);
    }

    override canMove(from: number, to: number) : boolean {
        const diff = Math.abs(from - to);

        return diff % 7 === 0 || diff % 9 === 0;
    }
}