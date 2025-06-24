import { Component, inject, OnInit } from '@angular/core';
import { ActivatedRoute, Router, RouterOutlet } from '@angular/router';
import { NgFor, NgIf } from '@angular/common';
import { Square } from './square';
import { CheckersService } from './checkers.service';
import { ApiResult } from './api-result';

@Component({
  selector: 'app-root',
  imports: [RouterOutlet, NgFor, NgIf],
  templateUrl: './app.component.html',
  styleUrl: './app.component.css'
})
export class AppComponent implements OnInit {
  title = 'checkers-app';
  board: Map<number, Square[]>;
  boardEntries: [number, Square[]][] = [];
  
  private readonly route = inject(ActivatedRoute);
  private readonly router = inject(Router);

  constructor(private checkersService: CheckersService) {
    this.board = new Map<number, Square[]>();
    this.board.set(1, [
      { position: '', color: 'light', piece: '' },
      { position: '1', color: 'dark', piece: 'red_piece' },
      { position: '', color: 'light', piece: '' },
      { position: '2', color: 'dark', piece: 'red_piece' },
      { position: '', color: 'light', piece: '' },
      { position: '3', color: 'dark', piece: 'red_piece' }, 
      { position: '', color: 'light', piece: '' },
      { position: '4', color: 'dark', piece: 'red_piece' },
    ]);

    this.board.set(2, [
      { position: '5', color: 'dark', piece: 'red_piece' },
      { position: '', color: 'light', piece: '' },
      { position: '6', color: 'dark', piece: 'red_piece' },
      { position: '', color: 'light', piece: '' },
      { position: '7', color: 'dark', piece: 'red_piece' },
      { position: '', color: 'light', piece: '' },
      { position: '8', color: 'dark', piece: 'red_piece' },
      { position: '', color: 'light', piece: '' },
    ]);

    this.board.set(3, [
      { position: '', color: 'light', piece: '' },
      { position: '9', color: 'dark', piece: 'red_piece' },
      { position: '', color: 'light', piece: '' },
      { position: '10', color: 'dark', piece: 'red_piece' },
      { position: '', color: 'light', piece: '' },
      { position: '11', color: 'dark', piece: 'red_piece' },
      { position: '', color: 'light', piece: '' },
      { position: '12', color: 'dark', piece: 'red_piece' },
    ]);

    this.board.set(4, [
      { position: '13', color: 'dark', piece: '' },
      { position: '', color: 'light', piece: '' },
      { position: '14', color: 'dark', piece: '' },
      { position: '', color: 'light', piece: '' },
      { position: '15', color: 'dark', piece: '' },
      { position: '', color: 'light', piece: '' },
      { position: '16', color: 'dark', piece: '' },
      { position: '', color: 'light', piece: '' },
    ]);
    
    this.board.set(5, [
      { position: '', color: 'light', piece: '' },
      { position: '17', color: 'dark', piece: '' },
      { position: '', color: 'light', piece: '' },
      { position: '18', color: 'dark', piece: '' },
      { position: '', color: 'light', piece: '' },
      { position: '19', color: 'dark', piece: '' },
      { position: '', color: 'light', piece: '' },
      { position: '20', color: 'dark', piece: '' },
    ]);

    this.board.set(6, [
       { position: '21', color: 'dark', piece: 'black_piece' },
       { position: '', color: 'light', piece: '' },
       { position: '22', color: 'dark', piece: 'black_piece' },
       { position: '', color: 'light', piece: '' },
       { position: '23', color: 'dark', piece: 'black_piece' },
       { position: '', color: 'light', piece: '' },
       { position: '24', color: 'dark', piece: 'black_piece' },
       { position: '', color: 'light', piece: '' },
    ]);

    this.board.set(7, [
        { position: '', color: 'light', piece: '' },
        { position: '25', color: 'dark', piece: 'black_piece' },
        { position: '', color: 'light', piece: '' },
        { position: '26', color: 'dark', piece: 'black_piece' },
        { position: '', color: 'light', piece: '' },
        { position: '27', color: 'dark', piece: 'black_piece' },
        { position: '', color: 'light', piece: '' },
        { position: '28', color: 'dark', piece: 'black_piece' },
    ]);
    
    this.board.set(8, [
      { position: '29', color: 'dark', piece: 'black_piece' },
      { position: '', color: 'light', piece: '' },
      { position: '30', color: 'dark', piece: 'black_piece' },
      { position: '', color: 'light', piece: '' },
      { position: '31', color: 'dark', piece: 'black_piece' },
      { position: '', color: 'light', piece: '' },
      { position: '32', color: 'dark', piece: 'black_piece' },
      { position: '', color: 'light', piece: '' }
    ]);

    this.boardEntries = Array.from(this.board.entries());
  }

  ngOnInit(): void {
    console.log('ng init');
    const gameId = this.route.snapshot.paramMap.get('id');
    console.log(gameId);

    if (!!gameId) {
      console.log('loading game');
    }
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
