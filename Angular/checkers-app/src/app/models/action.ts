import { Piece } from "./piece";

export class Action {
    private _type: ActionType;
    private _position: string;
    private _piece: Piece | null;

    constructor(type: ActionType, position: string, piece: Piece | null) {
        this._type = type;
        this._position = position;
        this._piece = piece;
    }

    get type(): ActionType {
        return this._type;
    }

    get position(): string {
        return this._position;
    }

    get pieceColor(): Piece | null {
        return this._piece;
    }
}

export class ActionType {
    static readonly MOVE = 'move';
    static readonly SELECT = 'select';
    static readonly UNSELECT = 'unselect';
}