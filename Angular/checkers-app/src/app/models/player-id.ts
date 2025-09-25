import { nanoid } from "nanoid";

export class PlayerId {
    private _id: string;

    constructor(id: string) {
        this._id = id;
    }

    get id(): string {
        return this._id;
    }

    public static generate(): PlayerId {
        return new PlayerId(nanoid());
    }
}