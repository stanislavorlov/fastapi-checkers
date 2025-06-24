import { Component, inject, OnInit, Renderer2 } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { NgFor, NgIf } from '@angular/common';
import { Square } from './square';
import { CheckersService } from './services/checkers.service';
import { ApiResult } from './models/api-result';
import { Board } from './models/board';

@Component({
  selector: 'app-root',
  imports: [NgFor, NgIf],
  templateUrl: './app.component.html',
  styleUrl: './app.component.css'
})
export class AppComponent implements OnInit {
  title = 'checkers-app';
  board: Board;
  
  private readonly route = inject(ActivatedRoute);
  private readonly router = inject(Router);

  constructor(private renderer: Renderer2, private checkersService: CheckersService) {
    this.board = new Board();
  }

  ngOnInit(): void {
    this.route.queryParamMap.subscribe(params => {
      const id = params.get('id');
      
      if (!!id) {
        this.board.load();
      }
    });
  }

  clickBoard(event: Event, square: Square): void {
    this.board.click(square);
  }

  newGame(): void {
    this.checkersService.newGame('New Game', new Date()).subscribe((game_id: ApiResult<string>) => {
      if (!!game_id) {
        this.router.navigate(['/'], {
          queryParams: { id: game_id }
        });
      }
    });
  }
}
