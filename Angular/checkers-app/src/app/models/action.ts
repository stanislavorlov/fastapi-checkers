export class Action {
    private _type: ActionType;
    private _square: string;
    private _playerId: string; // Player ID for the game

    constructor(type: ActionType, square: string, playerId: string) {
        this._type = type;
        this._square = square;
        this._playerId = playerId;
    }

    get playerId(): string {
        return this._playerId;
    }

    get type(): ActionType {
        return this._type;
    }

    get square(): string {
        return this._square;
    }
}

export enum ActionType {
    MOVE = 'move',
    SELECT = 'select',
    UNSELECT = 'unselect',
    CAPTURE = 'capture',
    PROMOTE = 'promote',
}