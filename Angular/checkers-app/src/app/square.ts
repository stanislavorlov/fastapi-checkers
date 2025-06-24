export class Square {
    private _position : string;
    private _color: string;
    private _piece: string;

    constructor(pos: string, col: string, piece: string) {
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