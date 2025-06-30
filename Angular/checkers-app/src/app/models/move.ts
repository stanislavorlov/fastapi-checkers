import { Action, ActionType } from "./action";
import { Piece } from "./piece";

export class Move extends Action {
    private _to: string;
    private _piece: Piece;
    
    constructor(from: string, to: string, playerId: string, piece: Piece) {
        super(ActionType.MOVE, from, playerId);
        this._to = to;
        this._piece = piece;
    }

    get to(): string {
        return this._to;
    }

    get piece(): Piece {
        return this._piece;
    }
}