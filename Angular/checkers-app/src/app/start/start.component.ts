import { Component } from '@angular/core';
import { CheckersService } from '../services/checkers.service';
import { Router } from '@angular/router';
import { ApiResult } from '../models/api-result';
import { NgIf } from '@angular/common';
import { NewGameFactory } from '../models/new-game-factory';
import { SessionStorageService } from '../services/session-storage.service';

@Component({
  selector: 'app-start',
  imports: [NgIf],
  templateUrl: './start.component.html',
  styleUrl: './start.component.css'
})
export class StartComponent {
  gameMode?: 'single' | 'multi' | 'online' | null;
  singleSide?: 'red' | 'black' | null;
  gameMenu: boolean;

  constructor(private checkersService: CheckersService, private sessionService: SessionStorageService, private router: Router) {
    this.gameMode = null;
    this.gameMenu = true;
  }

  choosePlayMode(mode: 'single' | 'multi' | 'online'): void {
    this.gameMode = mode;
  }

  singleModeColor(color: 'red' | 'black'): void {
    this.singleSide = color;
  }

  newGame(): void {
    const playerId = this.sessionService.getItem(SessionStorageService.PLAYER_ID_KEY)!;
    const newGame = NewGameFactory.createGame(playerId, this.gameMode!, this.singleSide || null);

    this.checkersService.newGame(newGame).subscribe((game_id: ApiResult<string>) => {
      if (!!game_id) {
        this.router.navigate(['/', game_id], { queryParams: {} });
      }
    });
  }

  backMenu(): void {
    //this.gameMenu = true;
    this.gameMode = null;
    this.singleSide = null;

    this.router.navigate(['/'], { queryParams: {} });
    //this.closeWebSocket();
  }
}
