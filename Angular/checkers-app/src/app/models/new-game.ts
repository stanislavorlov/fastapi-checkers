export class Player {
    public player_id: string;
    public side: string;

    public constructor(player_id: string, side: string) {
        this.player_id = player_id;
        this.side = side;
    }
}

export class NewGame {
    public name: string;
    public started: Date;
    public mode: 'single' | 'multi' | 'online';
    public dark_player: string | null = null;
    public light_player: string | null = null;

    public constructor(name: string, started: Date, mode: 'single' | 'multi' | 'online') {
        this.name = name;
        this.started = started;
        this.mode = mode;
    }
}