import { Component, OnInit } from '@angular/core';
import { CheckersService } from '../services/checkers.service';
import { ApiResult } from '../models/api-result';
import { Router } from '@angular/router';
import { NgIf } from '@angular/common';
import { LocalStorageService } from '../services/local-storage.service';
import { UserService } from '../services/user.service';

@Component({
  selector: 'app-game',
  imports: [NgIf],
  templateUrl: './choose-game.component.html',
  styleUrl: './choose-game.component.css'
})
export class GameComponent implements OnInit {
  gameMode?: 'computer' | 'online' | null;
  singleSide?: 'red' | 'black' | null;

  constructor(
    private checkersService: CheckersService,
    private localStorageService: LocalStorageService,
    private userService: UserService,
    private router: Router) {
    this.gameMode = null;
  }

  async ngOnInit(): Promise<void> {
    await this.userService.init();
  }

  choosePlayMode(mode: 'computer' | 'online'): void {
    this.gameMode = mode;
  }

  computerModeColor(color: 'red' | 'black'): void {
    this.singleSide = color;
  }

  newGame(): void {
    /*const currentPlayer = this.userService.currentPlayer;
    if (!currentPlayer) {
      console.error('Player data is not available.');
      return;
    }*/

    //const newGame = NewGameFactory.createGame(currentPlayer.player_id, currentPlayer.is_guest, this.gameMode!, this.singleSide || null);

    switch (this.gameMode) {
      case 'computer':

        this.checkersService.requestComputerGame().subscribe({
          next: (game_id: ApiResult<string>) => {
            if (!!game_id) {
              this.router.navigate(['/', game_id], { queryParams: {} });
            }
          }
        });

        break;
      case 'online':

        this.checkersService.requestOnlineGame().subscribe({
          next: (game_id: ApiResult<string>) => {
            if (!!game_id) {
              this.router.navigate(['/', game_id], { queryParams: {} });
            }
          }
        });

        break;
      default:
        console.error('Invalid game mode selected.');
        return;
    }
  }

  backMenu(): void {
    this.router.navigate(['/'], { queryParams: {} });
  }
}
