import { Component } from '@angular/core';
import { CheckersService } from '../services/checkers.service';
import { Router } from '@angular/router';
import { ApiResult } from '../models/api-result';
import { NgIf } from '@angular/common';
import { NewGameFactory } from '../models/new-game-factory';
import { UserService } from '../services/user.service';

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

  constructor(private checkersService: CheckersService, private userService: UserService, private router: Router) {
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
    const playerId = this.userService.currentPlayer?.player_id || '';
    if (!playerId) {
      console.error('Player ID is not available.');
      return;
    }

    const newGame = NewGameFactory.createGame(playerId, this.gameMode!, this.singleSide || null);

    this.checkersService.newGame(newGame).subscribe((game_id: ApiResult<string>) => {
      if (!!game_id) {
        this.router.navigate(['/', game_id], { queryParams: {} });
      }
    });
  }

  logIn(): void {
    this.router.navigate(['/account/login'], { queryParams: {} });
  }

  signUp(): void {
    this.router.navigate(['/account/signup'], { queryParams: {} });
  }

  backMenu(): void {
    this.gameMode = null;
    this.singleSide = null;

    this.router.navigate(['/'], { queryParams: {} });
  }
}
