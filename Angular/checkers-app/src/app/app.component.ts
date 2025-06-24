import { Component } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { NgFor, NgIf } from '@angular/common';
import { Square } from './square';

@Component({
  selector: 'app-root',
  imports: [RouterOutlet, NgFor, NgIf],
  templateUrl: './app.component.html',
  styleUrl: './app.component.css'
})
export class AppComponent {
  title = 'checkers-app';
  board: Map<number, Square[]>;
  boardEntries: [number, Square[]][] = [];

  constructor() {
    this.board = new Map<number, Square[]>();
    this.board.set(1, [
      { position: 'a1', color: 'light', piece: '' },
      { position: 'b1', color: 'dark', piece: 'red_piece' },
      { position: 'c1', color: 'light', piece: '' },
      { position: 'd1', color: 'dark', piece: 'red_piece' },
      { position: 'e1', color: 'light', piece: '' },
      { position: 'f1', color: 'dark', piece: 'red_piece' }, 
      { position: 'g1', color: 'light', piece: '' },
      { position: 'h1', color: 'dark', piece: 'red_piece' },
    ]);

    this.board.set(2, [
      { position: 'a2', color: 'dark', piece: 'red_piece' },
      { position: 'b2', color: 'light', piece: '' },
      { position: 'c2', color: 'dark', piece: 'red_piece' },
      { position: 'd2', color: 'light', piece: '' },
      { position: 'e2', color: 'dark', piece: 'red_piece' },
      { position: 'f2', color: 'light', piece: '' },
      { position: 'g2', color: 'dark', piece: 'red_piece' },
      { position: 'h2', color: 'light', piece: '' },
    ]);

    this.board.set(3, [
      { position: 'a3', color: 'light', piece: '' },
      { position: 'b3', color: 'dark', piece: 'red_piece' },
      { position: 'c3', color: 'light', piece: '' },
      { position: 'd3', color: 'dark', piece: 'red_piece' },
      { position: 'e3', color: 'light', piece: '' },
      { position: 'f3', color: 'dark', piece: 'red_piece' },
      { position: 'g3', color: 'light', piece: '' },
      { position: 'h3', color: 'dark', piece: 'red_piece' },
    ]);

    this.board.set(4, [
      { position: 'a4', color: 'dark', piece: '' },
      { position: 'b4', color: 'light', piece: '' },
      { position: 'c4', color: 'dark', piece: '' },
      { position: 'd4', color: 'light', piece: '' },
      { position: 'e4', color: 'dark', piece: '' },
      { position: 'f4', color: 'light', piece: '' },
      { position: 'g4', color: 'dark', piece: '' },
      { position: 'h4', color: 'light', piece: '' },
    ]);
    
    this.board.set(5, [
      { position: 'a5', color: 'light', piece: '' },
      { position: 'b5', color: 'dark', piece: '' },
      { position: 'c5', color: 'light', piece: '' },
      { position: 'd5', color: 'dark', piece: '' },
      { position: 'e5', color: 'light', piece: '' },
      { position: 'f5', color: 'dark', piece: '' },
      { position: 'g5', color: 'light', piece: '' },
      { position: 'h5', color: 'dark', piece: '' },
    ]);

    this.board.set(6, [
       { position: 'a6', color: 'dark', piece: 'black_piece' },
       { position: 'b6', color: 'light', piece: '' },
       { position: 'c6', color: 'dark', piece: 'black_piece' },
       { position: 'd6', color: 'light', piece: '' },
       { position: 'e6', color: 'dark', piece: 'black_piece' },
       { position: 'f6', color: 'light', piece: '' },
       { position: 'g6', color: 'dark', piece: 'black_piece' },
       { position: 'h6', color: 'light', piece: '' },
    ]);

    this.board.set(7, [
        { position: 'a7', color: 'light', piece: '' },
        { position: 'b7', color: 'dark', piece: 'black_piece' },
        { position: 'c7', color: 'light', piece: '' },
        { position: 'd7', color: 'dark', piece: 'black_piece' },
        { position: 'e7', color: 'light', piece: '' },
        { position: 'f7', color: 'dark', piece: 'black_piece' },
        { position: 'g7', color: 'light', piece: '' },
        { position: 'h7', color: 'dark', piece: 'black_piece' },
    ]);
    
    this.board.set(8, [
      { position: 'a8', color: 'dark', piece: 'black_piece' },
      { position: 'b8', color: 'light', piece: '' },
      { position: 'c8', color: 'dark', piece: 'black_piece' },
      { position: 'd8', color: 'light', piece: '' },
      { position: 'e8', color: 'dark', piece: 'black_piece' },
      { position: 'f8', color: 'light', piece: '' },
      { position: 'g8', color: 'dark', piece: 'black_piece' },
      { position: 'h8', color: 'light', piece: '' }
    ]);

    this.boardEntries = Array.from(this.board.entries());
  }

  clickBoard(square: Square): void {
    console.log(square);
  }
}
