import { Component, inject, OnDestroy, OnInit, Renderer2 } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { NgFor, NgIf } from '@angular/common';
import { Square } from './models/square';
import { CheckersService } from './services/checkers.service';
import { ApiResult } from './models/api-result';
import { Board } from './models/board';
import { ActionType } from './models/action';
import { Move } from './models/move';
import { Game } from './models/game';
import { Piece } from './models/piece';
import { Board2 } from './models/board-reactoring';

@Component({
  selector: 'app-root',
  imports: [NgFor, NgIf],
  templateUrl: './app.component.html',
  styleUrl: './app.component.css'
})
export class AppComponent implements OnInit, OnDestroy {
  title = 'checkers-app';
  board: Board2;
  pieces: Map<Square, Piece>;
  
  private readonly route = inject(ActivatedRoute);
  private readonly router = inject(Router);
  private webSocket?: WebSocket;

  constructor(private checkersService: CheckersService) {
    this.board = new Board2();
    this.pieces = new Map<Square, Piece>();
  }

  ngOnInit(): void {
    this.route.queryParamMap.subscribe(params => {
      const id = params.get('id');
      
      if (!!id) {
        this.checkersService.loadGame(id).subscribe((result: Game) => {
          if (!result) {
            console.error('Game not found or invalid response');
            return;
          }
          
          this.board.load(result);
          this.pieces = this.board.pieces;

          this.connectWebSocket(id);
        });
      }
    });
  }

  ngOnDestroy(): void {
    this.closeWebSocket();
  }

  closeWebSocket(): void {
    if (this.webSocket) {
      this.webSocket.close();
      this.webSocket = undefined;
    }
  }

  connectWebSocket(gameId: string): void {
    this.webSocket = new WebSocket(`ws://localhost:8000/ws/${gameId}`);

    this.webSocket.onopen = (ev: Event) => {
      console.log('WebSocket connection established');
    };

    this.webSocket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      console.log('Received data:', data);
      
      switch (data.event_type) {
        case 'captured':
          let capturedSquare = data.captured_at;
          break;
        case 'moved':
          let [from, to] = [data.moved_from, data.moved_to];
          break;
        case 'turn':
          let turn = data.current_turn;
          break;
      }

      if (data._type === 'move') {
        const move = new Move(data._from, data._to, data._playerId, data._piece);
        
        this.board.reply(move);
      }
    };

    this.webSocket.onclose = () => {
      console.log('WebSocket connection closed');
    };

    this.webSocket.onerror = (error) => {
      console.error('WebSocket error:', error);
    };
  }

  clickBoard(square: Square): void {

    if (square.canSelect) {
      let action = this.board.click(square);

      if (action.type == ActionType.MOVE || action.type == ActionType.CAPTURE || action.type == ActionType.PROMOTE) {
        let from = this.board.getHistory().slice(-2)[0];
        let to = this.board.getHistory().slice(-2)[1];

        if (this.webSocket && this.webSocket.readyState === WebSocket.OPEN) {
          this.webSocket.send(JSON.stringify({ _playerId: action.playerId, _type: action.type, _from: from.square, to: to.square }));
        }
      }
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
