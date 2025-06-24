import { Component, inject, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { NgFor, NgIf } from '@angular/common';
import { Square } from './square';
import { CheckersService } from './checkers.service';
import { ApiResult } from './api-result';
import { Board } from './board';

@Component({
  selector: 'app-root',
  imports: [NgFor, NgIf],
  templateUrl: './app.component.html',
  styleUrl: './app.component.css'
})
export class AppComponent implements OnInit {
  title = 'checkers-app';
  boardEntries: [number, Square[]][] = [];
  
  private readonly route = inject(ActivatedRoute);
  private readonly router = inject(Router);

  constructor(private checkersService: CheckersService) {
  }

  ngOnInit(): void {
    const gameId = this.route.snapshot.paramMap.get('id');
    let board = new Board();

    if (!!gameId) {
      board.load();
    }

    this.boardEntries = board.getView();
  }

  clickBoard(square: Square): void {
    console.log(square);
  }

  newGame(): void {
    this.checkersService.newGame('New Game', new Date()).subscribe((game_id: ApiResult<string>) => {
      if (!!game_id) {
        this.router.navigate([
          '/',
          game_id
        ]);
      }
    });
  }
}
