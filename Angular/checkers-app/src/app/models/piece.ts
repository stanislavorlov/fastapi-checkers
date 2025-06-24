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
}

export class Queen extends Piece {
    constructor(color: PieceColor) {
        super(color);
    }
}