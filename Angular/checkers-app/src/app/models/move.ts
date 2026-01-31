import { PieceColor } from "./piece-color";

export class Move {
    private _path: string[];
    private _captured: string[];
    private _playerId: string;
    private _playerSide: PieceColor;
    private _isCapture: boolean = false;

    constructor(playerId: string, playerSide: PieceColor) {
        this._path = [];
        this._captured = [];
        this._playerId = playerId;
        this._playerSide = playerSide;
    }

    get playerId(): string {
        return this._playerId;
    }

    get playerSide(): string {
        return this._playerSide == PieceColor.BLACK ? 'Dark' : 'Light';
    }

    get move(): string {
        if (this._path.length < 2) {
            return this._path.join("");
        }
        const separator = this._isCapture ? "x" : "-";
        return this._path.join(separator);
    }

    get captured(): string[] {
        return this._captured;
    }

    public addSquare(square: string): void {
        if (this._path.length === 0 || this._path[this._path.length - 1] !== square) {
            this._path.push(square);
        }
    }

    public addCapture(square: string, captured: string): void {
        this._isCapture = true;
        this.addSquare(square);
        if (!this._captured.includes(captured)) {
            this._captured.push(captured);
        }
    }

    public toJSONstring(): string {
        return JSON.stringify({
            playerId: this.playerId,
            move: this.move,
            captured: this.captured
        });
    }
}