import { Component, inject } from '@angular/core';
import { CheckersService } from '../services/checkers.service';
import { Router } from '@angular/router';
import { ApiResult } from '../models/api-result';
import { AsyncPipe, NgIf } from '@angular/common';
import { NewGameFactory } from '../models/new-game-factory';
import { UserService } from '../services/user.service';

@Component({
  selector: 'app-start',
  imports: [NgIf, AsyncPipe],
  templateUrl: './start.component.html',
  styleUrl: './start.component.css'
})
export class StartComponent {
  gameMode?: 'single' | 'online' | null;
  singleSide?: 'red' | 'black' | null;
  gameMenu: boolean;
  private userService: UserService = inject(UserService);
  player$ = this.userService.player$;

  constructor(private checkersService: CheckersService, private router: Router) {
    this.gameMode = null;
    this.gameMenu = true;
  }

  choosePlayMode(mode: 'single' | 'online'): void {
    this.gameMode = mode;
  }

  singleModeColor(color: 'red' | 'black'): void {
    this.singleSide = color;
  }

  newGame(): void {
    const currentPlayer = this.userService.currentPlayer;
    if (!currentPlayer) {
      console.error('Player data is not available.');
      return;
    }

    const newGame = NewGameFactory.createGame(currentPlayer.player_id, currentPlayer.is_guest, this.gameMode!, this.singleSide || null);

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

  logOut(): void {
    this.userService.logout();
    this.gameMode = null;
    this.singleSide = null;
    this.router.navigate(['/'], { queryParams: {} });
  }

  backMenu(): void {
    this.gameMode = null;
    this.singleSide = null;

    this.router.navigate(['/'], { queryParams: {} });
  }
}
