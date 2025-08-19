import { Direction } from "./direction";
import { PieceColor } from "./piece";

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

    get siblings(): Map<Direction, Square> {
        return this._siblings;
    }

    abstract get canSelect(): boolean;

    filterSiblings(pieceColor: PieceColor): [Direction, Square][] {
        switch (pieceColor) {
            case PieceColor.RED:
                return [...Array.from(this._siblings).filter(sibling => sibling[0] == Direction.UP_LEFT || sibling[0] == Direction.UP_RIGHT)];
            case PieceColor.BLACK:
                return [...Array.from(this._siblings).filter(sibling => sibling[0] == Direction.DOWN_LEFT || sibling[0] == Direction.DOWN_RIGHT)];
            default:
                return [];
        }
    }

    leftSibling(pieceColor: PieceColor): Square | undefined {
        switch (pieceColor) {
            case PieceColor.RED:
                return this._siblings.get(Direction.UP_LEFT);
            case PieceColor.BLACK:
                return this._siblings.get(Direction.DOWN_LEFT);
            default:
                return undefined;
        }
    }

    rightSibling(pieceColor: PieceColor): Square | undefined {
        switch (pieceColor) {
            case PieceColor.RED:
                return this._siblings.get(Direction.UP_RIGHT);
            case PieceColor.BLACK:
                return this._siblings.get(Direction.DOWN_RIGHT);
            default:
                return undefined;
        }
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