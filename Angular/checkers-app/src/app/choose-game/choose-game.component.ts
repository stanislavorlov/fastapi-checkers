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
    if (mode === 'online') {
      this.startNewGame();
    }
  }

  computerModeColor(color: 'red' | 'black'): void {
    this.singleSide = color;
    this.startNewGame();
  }

  startNewGame(): void {
    const request$ = this.gameMode === 'computer'
      ? this.checkersService.requestComputerGame(this.singleSide!)
      : this.checkersService.requestOnlineGame();

    request$.subscribe({
      next: (game_id: ApiResult<string>) => {
        if (game_id) {
          this.router.navigate(['/', game_id], { queryParams: {} });
        }
      },
      error: (err) => {
        console.error('Failed to start game:', err);
      }
    });
  }

  backMenu(): void {
    if (this.gameMode) {
      this.gameMode = null;
      this.singleSide = null;
    } else {
      this.router.navigate(['/'], { queryParams: {} });
    }
  }
}
