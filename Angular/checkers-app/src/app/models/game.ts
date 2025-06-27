export interface Game {
     game_id: string;
     name: string;
     started: Date;
     history: HistoryEntry[];
}
export interface HistoryEntry {
    player_id: string;
    event_type: string;
    from_: string;
    to_: string;
}