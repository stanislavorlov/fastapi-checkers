import { Direction } from "./direction";
import { PieceColor } from "./piece-color";

export abstract class Square {
    
    private _selected: boolean = false;
    protected _id: string;
    protected _color: string;
    protected _siblings: Map<Direction, Square> = new Map<Direction, Square>();

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

    siblings(directions: Direction[]): [Direction, Square][] {
        return directions
            .filter(dir => this._siblings.get(dir) !== undefined)
            .map(dir => [dir, this._siblings.get(dir) as Square]);
    }

    abstract get canSelect(): boolean;

    sibling(direction: Direction): Square | undefined {
        return this._siblings.get(direction);
    }

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

    addSibling(direction: Direction, square: Square): void {
        this._siblings.set(direction, square);
    }
}

export class WhiteSquare extends Square {

    constructor(id: string) {
        super(id, 'light');
    }

    override get canSelect(): boolean {
        return false;
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