export class Move {
    private _squares: string[];
    private _captured: string[];
    private _playerId: string;

    constructor(playerId: string) {
        this._squares = [];
        this._captured = [];
        this._playerId = playerId;
    }

    get playerId(): string {
        return this._playerId;
    }

    get move(): string {
        return this._squares.join("");
    }

    get captured(): string[] {
        return this._captured;
    }

    public addSquare(square: string): void {
        if (this._squares.some(s => s === "x")) {
            throw new Error("Cannot add square after capture without adding capture first");
        }

        if (this._squares.length === 3) {
            throw new Error("Cannot add more than two moves without capture");
        }

        if (this._squares.length > 0) {
            this._squares.push("-");
        }

        this._squares.push(square);
    }

    public addCapture(square: string, captured: string): void {
        if (this._squares.some(s => s === "-")) {
            throw new Error("Cannot add capture after move without adding move first");
        }

        if (this._squares.length > 0) {
            this._squares.push("x");
        }
        this._squares.push(square);
        this._captured.push(captured);
    }

    public toJSONstring(): string {
        return JSON.stringify({
            playerId: this.playerId,
            move: this.move,
            captured: this.captured
        });
    }
}