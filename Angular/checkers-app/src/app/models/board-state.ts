import { PieceColor } from "./piece-color";
import { Square } from "./square";

export class BoardState {
    private _turn: PieceColor = PieceColor.BLACK;
    private _playerColor?: PieceColor;
    private _started: boolean = false;
    private _finished: boolean = false;
    private _selectedSquare: Square | null = null;
    private _activeJumpingPiece: Square | null = null;
    private _forcedCapture: boolean = false;

    get turn(): PieceColor { return this._turn; }
    get playerColor(): PieceColor | undefined { return this._playerColor; }
    get started(): boolean { return this._started; }
    get finished(): boolean { return this._finished; }
    get selectedSquare(): Square | null { return this._selectedSquare; }
    get activeJumpingPiece(): Square | null { return this._activeJumpingPiece; }
    get forcedCapture(): boolean { return this._forcedCapture; }

    set turn(value: PieceColor) { this._turn = value; }
    set playerColor(value: PieceColor | undefined) { this._playerColor = value; }
    set started(value: boolean) { this._started = value; }
    set finished(value: boolean) { this._finished = value; }
    set forcedCapture(value: boolean) { this._forcedCapture = value; }

    public reset() {
        this._turn = PieceColor.BLACK;
        this._selectedSquare = null;
        this._activeJumpingPiece = null;
        this._finished = false;
        this._forcedCapture = false;
    }

    public select(square: Square) {
        this._selectedSquare = square;
        square.select();
    }

    public unselect() {
        if (this._selectedSquare) {
            this._selectedSquare.unselect();
            this._selectedSquare = null;
        }
        this._activeJumpingPiece = null;
    }

    public setActiveJumpingPiece(square: Square) {
        this._activeJumpingPiece = square;
        square.select();
    }

    public clearActiveJumpingPiece() {
        if (this._activeJumpingPiece) {
            this._activeJumpingPiece.unselect();
            this._activeJumpingPiece = null;
        }
    }

    public switchTurn() {
        this._turn = this._turn === PieceColor.BLACK ? PieceColor.RED : PieceColor.BLACK;
        this._selectedSquare = null;
        this._activeJumpingPiece = null;
    }

    public isYourTurn(): boolean {
        return this._playerColor === this._turn;
    }

    public canInteract(): boolean {
        return this._started && !this._finished && this.isYourTurn();
    }
}
