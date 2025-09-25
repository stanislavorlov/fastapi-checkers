import { Component, inject, OnDestroy, OnInit } from '@angular/core';
import { ActionType } from '../models/action';
import { ActivatedRoute, Router } from '@angular/router';
import { Move } from '../models/move';
import { Square } from '../models/square';
import { Board } from '../models/board';
import { Piece } from '../models/piece';
import { NgFor, NgIf } from '@angular/common';
import { SessionStorageService } from '../services/session-storage.service';
import { CheckersService } from '../services/checkers.service';
import { Game } from '../models/game';

@Component({
  selector: 'app-play',
  imports: [NgFor, NgIf],
  templateUrl: './play.component.html',
  styleUrl: './play.component.css'
})
export class PlayComponent implements OnInit, OnDestroy {
  board: Board;
  pieces: Map<Square, Piece>;
  private readonly route = inject(ActivatedRoute);
  private readonly router = inject(Router);
  private webSocket?: WebSocket;

  gameId = this.route.snapshot.paramMap.get('id')!;
  gameMenu: boolean;
  gameMode?: 'single' | 'multi' | 'online' | null;
  singleSide?: 'red' | 'black' | null;
  playerId: string = '';
  playerSide?: 'red' | 'black';

  constructor(private checkersService: CheckersService, protected sessionStorage: SessionStorageService) {
    this.gameMenu = true;
    this.playerId = sessionStorage.getItem(SessionStorageService.PLAYER_ID_KEY)!;
    this.board = new Board(this.playerId, this.gameId);
    this.pieces = new Map<Square, Piece>();

    console.log("Game ID:", this.gameId);
    console.log("Player ID:", this.playerId);
  }

  ngOnInit(): void {
    if (!!this.gameId) {
      this.checkersService.loadGame(this.gameId).subscribe((result: Game) => {
        if (!result) {
          console.error('Game not found or invalid response');
          return;
        }

        // ToDo: display the payer side based on playerId and game data
        if (this.playerId === result.light_player) {
          this.playerSide = 'red';
        } else if (this.playerId === result.dark_player) {
          this.playerSide = 'black';
        } else {
          console.error('Player not part of this game');
          return;
        }
        
        this.board.load(result);
        this.pieces = this.board.pieces;

        this.connectWebSocket(this.gameId);
      });
    }
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

  backMenu(): void {
    this.gameMenu = true;
    this.gameMode = null;
    this.singleSide = null;

    this.router.navigate(['/'], { queryParams: {} });
    this.closeWebSocket();
  }

}
