import { Action, ActionType } from "./action";
import { Piece } from "./piece";

export class Move extends Action {
    private _to: string;
    
    constructor(from: string, to: string, playerId: string, piece: Piece | null) {
        super(ActionType.MOVE, from, playerId, piece);
        this._to = to;
    }

    get to(): string {
        return this._to;
    }
}