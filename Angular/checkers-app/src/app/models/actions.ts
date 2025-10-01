import { Action } from "./action";
import { Move } from "./move";

export class Actions {
    private _move: Move | null;
    private _action: Action | null;

    constructor(move: Move | null, action: Action | null) {
        this._move = move;
        this._action = action;
    }

    public get move(): Move | null {
        return this._move;
    }
    
    public get action(): Action | null {
        return this._action;
    }
}