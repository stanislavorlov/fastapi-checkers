import { Piece } from "./piece";

export abstract class Square {
    
    private _selected: boolean = false;
    protected _id: string;
    protected _color: string;

    constructor(id : string, color: string = 'light') {
        this._id = id;
        this._color = color;
    }

    get id() {
        return this._id;
    }

    get color() {
        return this._color;
    }

    get selected() {
        return this._selected;
    }

    abstract get canSelect(): boolean;

    select(): void {
        if (this.canSelect) {
            this._selected = true;
        }
    }

    unselect(): void {
        if (this.canSelect) {
            this._selected = false;
        }
    }
}

export class WhiteSquare extends Square {

    constructor(id: string) {
        super(id, 'light');
    }

    override get canSelect(): boolean {
        return false; // White squares cannot be selected in checkers
    }
}

export class BlackSquare extends Square {
    private _position: string;

    constructor(pos: string) {
        super(pos, 'dark');
        this._position = pos;
    }

    override get canSelect(): boolean {
        return !!this._position;
    }

    get position() {
        return this._position;
    }
}