import { Piece } from "./piece";
import { Square } from "./square";

/**
 * Represents a move of piece in the game.
 */
export class AvailableMove {
    protected _captured: CapturedPiece | null = null;

    constructor(public from: Square, public to: Square) {
        this.from = from;
        this.to = to;
    }

    get captured(): CapturedPiece | null {
        return this._captured;
    }
}

/**
 * Represents a capture move in the game, which includes the piece being captured.
 */
export class AvailableJump extends AvailableMove {
    constructor(from: Square, to: Square, captured: CapturedPiece) {
        super(from, to);
        this._captured = captured;
    }
}

export class CapturedPiece {
    constructor(public square: Square, public piece: Piece) {
        this.square = square;
        this.piece = piece;
    }
}