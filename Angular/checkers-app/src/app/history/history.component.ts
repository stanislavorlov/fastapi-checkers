import { Component, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { CheckersService } from '../services/checkers.service';
import { UserService } from '../services/user.service';
import { Game } from '../models/game';

@Component({
  selector: 'app-history',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './history.component.html',
  styleUrl: './history.component.css',
})
export class HistoryComponent implements OnInit {
  private readonly checkersService = inject(CheckersService);
  private readonly userService = inject(UserService);
  private readonly router = inject(Router);

  history: Game[] = [];
  loading: boolean = true;
  currentPlayerId: string | null = null;

  ngOnInit(): void {
    // Get current player ID for display logic
    this.userService.player$.subscribe(player => {
      if (player) {
        this.currentPlayerId = player.player_id;
      }
    });

    this.checkersService.getPlayerGames().subscribe({
      next: (history) => {
        this.history = history;
        this.loading = false;
      },
      error: (err) => {
        console.error('Failed to load history', err);
        this.loading = false;
      }
    });
  }

  getOpponent(game: Game): string {
    const players = [game.light_player, game.dark_player];
    const other = players.find((id: string) => id !== this.currentPlayerId) as string;
    if (!other) return 'Computer';

    return other;
  }

  getResult(game: Game): string {
    if (!game.finished_at) return 'In Progress';
    if (!game.result) return 'Draw';

    const result = game.result;
    if (!result.winner) return 'Draw';

    return (result.winner === this.currentPlayerId) ? 'Victory' : 'Defeat';
  }

  viewGame(gameId: string) {
    this.router.navigate([gameId])
      .then(success => {
        if (!success) console.warn('Navigation blocked');
      })
      .catch(error => {
        alert(`Failed to view game: ${error}`);
      });
  }

  goBack() {
    window.history.back();
  }
}
