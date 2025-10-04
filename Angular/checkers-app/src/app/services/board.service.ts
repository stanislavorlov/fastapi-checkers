import { Injectable } from '@angular/core';
import { Game } from '../models/game';

@Injectable({
  providedIn: 'root'
})
export class BoardService {

  constructor() { }

  createBoard() {
    // Logic to create and return a new board instance
  }

  loadBoard(game: Game) {
    // Logic to load a board from game data
  }
}
