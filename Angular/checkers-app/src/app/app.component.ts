import { Component, inject, OnInit, Renderer2 } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { NgFor, NgIf } from '@angular/common';
import { Square } from './square';
import { CheckersService } from './services/checkers.service';
import { ApiResult } from './models/api-result';
import { Board } from './models/board';
import { ActionType } from './models/action';

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
  private webSocket?: WebSocket;

  constructor(private renderer: Renderer2, private checkersService: CheckersService) {
    this.board = new Board();
  }

  ngOnInit(): void {
    this.route.queryParamMap.subscribe(params => {
      const id = params.get('id');
      
      if (!!id) {
        this.board.load();

        this.connectWebSocket(id);
      }
    });
  }

  connectWebSocket(gameId: string): void {
    this.webSocket = new WebSocket(`ws://localhost:8000/ws/${gameId}`);

    this.webSocket.onopen = () => {
      console.log('WebSocket connection established');
    };

    this.webSocket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      console.log('Received data:', data);
      // Handle incoming data and update the board as necessary
    };

    this.webSocket.onclose = () => {
      console.log('WebSocket connection closed');
    };

    this.webSocket.onerror = (error) => {
      console.error('WebSocket error:', error);
    };
  }

  clickBoard(square: Square): void {
    let action = this.board.click(square);

    if (action.type == ActionType.SELECT) {
      // from:
      // action.position
    } else if (action.type == ActionType.MOVE) {
      // to:
      // action.position

      let move = this.board.getHistory().slice(-1)[0];

      if (this.webSocket && this.webSocket.readyState === WebSocket.OPEN) {
        const message = {
          type: 'move',
          from: move.from,
          to: move.to,
          piece: square.piece
        };
        this.webSocket.send(JSON.stringify(message));
      }

    } else if (action.type == ActionType.UNSELECT) {
      // clear selection
    }
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
