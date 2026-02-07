import { Component, OnInit } from '@angular/core';
import { CheckersService } from '../services/checkers.service';
import { ApiResult } from '../models/api-result';
import { Router } from '@angular/router';
import { NgIf } from '@angular/common';
import { UserService } from '../services/user.service';
import { RequestGame } from '../models/request_game';
import { MatchmakingService } from '../services/matchmaking.service';
import { Subscription } from 'rxjs';

@Component({
  selector: 'app-game',
  imports: [NgIf],
  templateUrl: './choose-game.component.html',
  styleUrl: './choose-game.component.css'
})
export class GameComponent implements OnInit {
  gameMode?: 'computer' | 'online' | null;
  singleSide?: 'red' | 'black' | null;
  isWaiting: boolean = false;
  private matchSubscription?: Subscription;

  constructor(
    private checkersService: CheckersService,
    private userService: UserService,
    private matchmakingService: MatchmakingService,
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
    switch (this.gameMode) {
      case 'computer':
        let requestComputer = this.checkersService.requestComputerGame(this.singleSide!);

        requestComputer.subscribe({
          next: (game_id: ApiResult<string>) => {
            if (game_id) {
              this.router.navigate(['/', game_id], { queryParams: {} });
            }
          },
          error: (err) => {
            console.error('Failed to start game:', err);
          }
        });
        break;
      case 'online':
        this.isWaiting = true;
        let requestOnline = this.checkersService.requestOnlineGame();

        requestOnline.subscribe({
          next: (result: RequestGame) => {
            console.log('Request online result: ' + JSON.stringify(result));
            if (result && result.player_id) {
              console.log('Starting matchmaking listening for player ' + result.player_id);
              this.startMatchmakingListening(result.player_id);
            }
          },
          error: (err) => {
            console.error('Failed to start game:', err);
            this.isWaiting = false;
          }
        });
        break;
      default:
        throw new Error('Invalid game mode');
    }
  }

  backMenu(): void {
    if (this.isWaiting) {
      this.cancelWaiting();
      return;
    }
    if (this.gameMode) {
      this.gameMode = null;
      this.singleSide = null;
    } else {
      this.router.navigate(['/'], { queryParams: {} });
    }
  }

  private startMatchmakingListening(playerId: string): void {
    this.matchmakingService.connect(playerId);
    this.matchSubscription = this.matchmakingService.matchFound$.subscribe((gameId) => {
      this.isWaiting = false;
      this.matchmakingService.disconnect();
      this.router.navigate(['/', gameId]);
    });
  }

  private cancelWaiting(): void {
    this.isWaiting = false;
    this.matchmakingService.disconnect();
    if (this.matchSubscription) {
      this.matchSubscription.unsubscribe();
    }
  }

  ngOnDestroy(): void {
    this.cancelWaiting();
  }
}
