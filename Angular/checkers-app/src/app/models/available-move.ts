import { Piece } from "./piece";
import { Square } from "./square";

export class AvailableMove {
    constructor(public from: Square, public to: Square, public piece: CapturedPiece | undefined) {
        this.from = from;
        this.to = to;
        this.piece = piece;
    }
}

export class CapturedPiece {
    constructor(public square: Square, public piece: Piece) {
        this.square = square;
        this.piece = piece;
    }
}