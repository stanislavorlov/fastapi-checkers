import { Move } from "./move";

export abstract class WsMessage {
    abstract type: string;
    abstract data: any;

    public toJSON(): string {
        return JSON.stringify({
            type: this.type,
            data: this.data
        });
    }
}

export class MoveMessage extends WsMessage {
    type = 'move';
    constructor(public data: Move) {
        super();
    }
}

export class AbandonMessage extends WsMessage {
    type = 'abandon';
    data = null;
    constructor() {
        super();
    }
}
