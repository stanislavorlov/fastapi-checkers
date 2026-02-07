import { Injectable } from '@angular/core';
import { Subject, Observable } from 'rxjs';

@Injectable({
    providedIn: 'root'
})
export class MatchmakingService {
    private socket?: WebSocket;
    private matchFoundSubject = new Subject<string>();

    public matchFound$: Observable<string> = this.matchFoundSubject.asObservable();

    constructor() { }

    connect(playerId: string): void {
        if (this.socket) {
            this.socket.close();
        }

        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        // Use the same hostname as the application to support local network sharing
        const host = `${window.location.hostname}:8000`;
        this.socket = new WebSocket(`${protocol}//${host}/ws/matchmaking/${playerId}`);

        this.socket.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                if (data.type === 'match_found') {
                    this.matchFoundSubject.next(data.game_id);
                }
            } catch (e) {
                console.error('Error parsing matchmaking message', e);
            }
        };

        this.socket.onclose = () => {
            console.log('Matchmaking WebSocket closed');
        };

        this.socket.onerror = (error) => {
            console.error('Matchmaking WebSocket error', error);
        };
    }

    disconnect(): void {
        if (this.socket) {
            this.socket.close();
            this.socket = undefined;
        }
    }
}
