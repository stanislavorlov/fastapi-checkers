export interface Game {
    game_id: string;
    name: string;
    started: Date;
    mode: string;
    light_player: string;
    dark_player: string;
    history: HistoryEntry[];
    finished_at?: Date;
    result?: any;
}
export interface HistoryEntry {
    player_id: string;
    move: string;
    captures: string[];
    sequence: number;
}