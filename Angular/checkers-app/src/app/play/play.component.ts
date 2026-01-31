import { Component, inject, OnDestroy, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { Move } from '../models/move';
import { Square } from '../models/square';
import { Board } from '../models/board';
import { Piece } from '../models/piece';
import { NgFor, NgIf, TitleCasePipe, UpperCasePipe, SlicePipe } from '@angular/common';
import { CheckersService } from '../services/checkers.service';
import { Game } from '../models/game';
import { Subject } from 'rxjs';
import { UserService } from '../services/user.service';
import { PieceColor } from '../models/piece-color';

@Component({
  selector: 'app-play',
  imports: [NgFor, NgIf, TitleCasePipe, UpperCasePipe, SlicePipe],
  templateUrl: './play.component.html',
  styleUrl: './play.component.css'
})
export class PlayComponent implements OnInit, OnDestroy {
  board: Board;
  pieces: Map<Square, Piece>;
  private readonly route = inject(ActivatedRoute);
  private readonly router = inject(Router);
  private webSocket?: WebSocket;
  private event$: Subject<Move>;

  gameId = this.route.snapshot.paramMap.get('id')!;
  gameMenu: boolean;
  gameMode?: 'single' | 'multi' | 'online' | null;
  singleSide?: 'red' | 'black' | null;
  playerId: string = '';
  playerSide?: 'red' | 'black';
  opponentId?: string;
  opponentSide?: 'red' | 'black';

  constructor(private checkersService: CheckersService, private userService: UserService) {
    this.gameMenu = true;
    this.event$ = new Subject<Move>();
    this.playerId = this.userService.currentPlayer?.player_id || '';
    this.board = new Board(this.playerId, this.gameId, this.event$);
    this.pieces = new Map<Square, Piece>();

    console.log("Game ID:", this.gameId);
    console.log("Player ID:", this.playerId);
  }

  ngOnInit(): void {
    const gameId = this.gameId;

    if (!!gameId) {
      this.userService.player$.subscribe(player => {
        if (!player) return;

        this.playerId = player.player_id;
        this.board.playerId = player.player_id;

        this.checkersService.loadGame(gameId).subscribe((result: Game) => {
          if (!result) {
            console.error('Game not found or invalid response');
            return;
          }

          if (this.playerId === result.light_player) {
            this.playerSide = 'red';
            this.opponentSide = 'black';
            this.opponentId = result.dark_player;
          } else if (this.playerId === result.dark_player) {
            this.playerSide = 'black';
            this.opponentSide = 'red';
            this.opponentId = result.light_player;
          } else {
            console.error('Player not part of this game', this.playerId, result.light_player, result.dark_player);
            // return;
          }

          this.board.load(result);
          this.pieces = this.board.pieces;

          this.connectWebSocket(gameId);

          this.event$.asObservable().subscribe((move: Move) => {
            console.log('Move event:', move.toJSONstring());

            if (this.webSocket && this.webSocket.readyState === WebSocket.OPEN) {
              this.webSocket.send(move.toJSONstring());
            }
          });
        });
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

    this.webSocket.onopen = (event) => {
      console.log('WebSocket connection established');
    };

    this.webSocket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      console.log('Received data:', data);

      let dataSide = PieceColor.BLACK;  //"R" or "B"
      if (data.player_color === "R") {
        dataSide = PieceColor.RED;
      } else {
        dataSide = PieceColor.BLACK;
      }

      this.board.replay(data.pdn, data.captured, data.player_id, dataSide);
    };

    this.webSocket.onclose = () => {
      console.log('WebSocket connection closed');
    };

    this.webSocket.onerror = (error) => {
      console.error('WebSocket error:', error);
    };
  }

  clickBoard(square: Square): void {
    const isYourTurn = (this.playerSide === 'red' && this.board.turn === 'Red') ||
      (this.playerSide === 'black' && this.board.turn === 'Black');

    if (square.canSelect && isYourTurn) {
      this.board.click(square);
    }
  }

  backMenu(): void {
    if (window.confirm("Are you sure to cancel this game?")) {
      this.gameMenu = true;
      this.gameMode = null;
      this.singleSide = null;

      this.router.navigate(['/game'], { queryParams: {} });
      this.closeWebSocket();
    }
  }

}
