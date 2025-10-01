export class Move {
    private _squares: string[];

    constructor() {
        this._squares = [];
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

    public addCapture(square: string): void {
        if (this._squares.some(s => s === "-")) {
            throw new Error("Cannot add capture after move without adding move first");
        }

        if (this._squares.length > 0) {
            this._squares.push("x");
        }
        this._squares.push(square);
    }

    public toString(): string {
        return this._squares.join("");
    }
}