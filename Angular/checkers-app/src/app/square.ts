import { Piece } from "./models/piece";

export class Square {
    private _position : string;
    private _color: string;
    private _piece: Piece | null;

    constructor(pos: string, col: string, piece: Piece | null) {
        this._position = pos;
        this._color = col;
        this._piece = piece;
    }

    get position() {
        return this._position;
    }

    get color() {
        return this._color;
    }

    get piece() {
        return this._piece;
    }
}