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

  newGame(name: string, started: Date, mode: string, single_side?: 'red' | 'black') {
    return this.httpClient.post<ApiResult<string>>('/api/', {
      name: name,
      started: started,
      mode: mode,
      single_side: single_side
    });
  }

  loadGame(gameId: string) {
    return this.httpClient.get<Game>(`/api/${gameId}`);
  }
}
