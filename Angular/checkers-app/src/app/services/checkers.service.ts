import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { ApiResult } from '../models/api-result';
import { Game } from '../models/game';

@Injectable({
  providedIn: 'root'
})
export class CheckersService {

  constructor(private httpClient: HttpClient) {
  }

  requestOnlineGame() {
    return this.httpClient.post<ApiResult<string>>('/api/games/online', {});
  }

  requestComputerGame(singleSide: string) {
    return this.httpClient.post<ApiResult<string>>('/api/games/computer', { singleSide });
  }

  loadGame(gameId: string) {
    return this.httpClient.get<Game>(`/api/games/${gameId}`);
  }

  getPlayerGames() {
    return this.httpClient.get<Game[]>(`/api/history`);
  }

  getGameHistory(gameId: string) {
    return this.httpClient.get<Game>(`/api/history/${gameId}`);
  }
}
