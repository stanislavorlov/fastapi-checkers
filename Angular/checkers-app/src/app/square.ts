import { Piece } from "./models/piece";

export class Square {
    private _position : string;
    private _color: string;
    private _piece: Piece | null;
    private _selected: boolean;

    constructor(pos: string, col: string, piece: Piece | null) {
        this._position = pos;
        this._color = col;
        this._piece = piece;
        this._selected = false;
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

    get isSelected() {
        return this._selected;
    }

    switchPiece(piece: Piece | null): void {
        this._piece = piece;
    }

    select(): void {
        this._selected = true;
    }

    unselect(): void {
        this._selected = false;
    }
}