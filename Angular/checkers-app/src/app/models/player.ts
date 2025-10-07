import { PlayerId } from "./player-id";

export class Player {
    public player_id: string = '';
    public email: string = '';
    public first_name: string = '';
    public last_name: string = '';
    public country: string = '';
    public is_guest: boolean = false;

    constructor(init?: Partial<Player>) {
        Object.assign(this, init);
    }

    public get displayName(): string {
        if (this.first_name && this.last_name) {
            return `${this.first_name} ${this.last_name}`;
        } else if (this.first_name) {
            return this.first_name;
        } else {
            return this.email;
        }
    }
}
export class GuestPlayer extends Player {
    constructor() {
        super();
        const id = Date.now().toString();
        this.player_id = PlayerId.generate().id;
        this.email = `Guest${id}`;
        this.is_guest = true;
    }
}