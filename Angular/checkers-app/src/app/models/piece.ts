import { Dir } from "fs";
import { Direction } from "./direction";

export enum PieceColor {
    BLACK = 1,
    RED = 2
}

export class Piece {
    private _color: PieceColor;

    constructor(color: PieceColor) {
        this._color = color;
    }

    get image() : string {
        return this._color == PieceColor.BLACK ? 'black_piece' : 'red_piece';
    }

    get isRed() {
        return this._color === PieceColor.RED;
    }

    get color() {
        return this._color;
    }

    get moveDirections() : Direction[] {
        switch (this._color) {
            case PieceColor.BLACK:
                return [Direction.DOWN_LEFT, Direction.DOWN_RIGHT];
            case PieceColor.RED:
                return [Direction.UP_LEFT, Direction.UP_RIGHT];
            default:
                return [];
        }
    }
}

export class Queen extends Piece {
    constructor(color: PieceColor) {
        super(color);
    }

    override get image(): string {
        return this.color === PieceColor.BLACK ? 'black_queen' : 'red_queen';
    }

    override get moveDirections(): Direction[] {
        return [Direction.UP_LEFT, Direction.UP_RIGHT, Direction.DOWN_LEFT, Direction.DOWN_RIGHT];
    }
}