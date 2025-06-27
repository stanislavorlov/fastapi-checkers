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

  newGame(name: string, started: Date) {
    return this.httpClient.post<ApiResult<string>>('/api/', {
      name: name,
      started: started
    });
  }

  loadGame(gameId: string) {
    return this.httpClient.get<Game>(`/api/${gameId}`);
  }
}
