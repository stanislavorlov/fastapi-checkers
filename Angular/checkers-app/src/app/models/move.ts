import { Piece } from "./piece";

export class Move {
    private _from: string;
    private _to: string;
    private _piece: Piece | null;

    constructor(from: string, to: string, piece: Piece | null) {
        this._from = from;
        this._to = to;
        this._piece = piece;
    }

    get from(): string {
        return this._from;
    }

    get to(): string {
        return this._to;
    }

    get piece(): Piece | null {
        return this._piece;
    }
}