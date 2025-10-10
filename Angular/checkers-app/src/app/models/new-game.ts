export class GamePlayer {
    public player_id: string;
    public side: string;
    public requestor: boolean = false;
    public anonymous: boolean = false;

    public constructor(player_id: string, side: string, requestor: boolean = false, anonymous: boolean = false) {
        this.player_id = player_id;
        this.side = side;
        this.requestor = requestor;
        this.anonymous = anonymous;
    }
}

export class NewGame {
    public name: string;
    public started: Date;
    public mode: 'single' | 'multi' | 'online';
    public players: GamePlayer[] = [];

    public constructor(name: string, started: Date, mode: 'single' | 'multi' | 'online', players: GamePlayer[] = []) {
        this.name = name;
        this.started = started;
        this.mode = mode;
        this.players = players;
    }
}