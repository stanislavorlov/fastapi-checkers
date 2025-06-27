import { Piece } from "./piece";

export class Action {
    private _type: ActionType;
    private _from: string;
    private _piece: Piece | null;
    private _playerId: string; // Player ID for the game

    constructor(type: ActionType, position: string, playerId: string, piece: Piece | null) {
        this._type = type;
        this._from = position;
        this._playerId = playerId;
        this._piece = piece;
    }

    get playerId(): string {
        return this._playerId;
    }

    get type(): ActionType {
        return this._type;
    }

    get from(): string {
        return this._from;
    }

    get piece(): Piece | null {
        return this._piece;
    }
}

export class ActionType {
    static readonly MOVE = 'move';
    static readonly SELECT = 'select';
    static readonly UNSELECT = 'unselect';
}