import { Component, inject, OnInit } from '@angular/core';
import { CheckersService } from '../services/checkers.service';
import { Router } from '@angular/router';
import { ApiResult } from '../models/api-result';
import { AsyncPipe, NgIf } from '@angular/common';
//import { NewGameFactory } from '../models/new-game-factory';
import { UserService } from '../services/user.service';
import { Player } from '../models/player';

@Component({
  selector: 'app-start',
  imports: [NgIf, AsyncPipe],
  templateUrl: './start-page.component.html',
  styleUrl: './start-page.component.css'
})
export class StartComponent implements OnInit {


  gameMenu: boolean;
  private userService: UserService = inject(UserService);
  player$ = this.userService.player$;

  constructor(private router: Router) {
    this.gameMenu = true;
  }

  ngOnInit(): void {
    console.log('StartComponent initialized');
  }

  play(): void {
    this.router.navigate(['/game'], { queryParams: {} });
  }

  logIn(): void {
    this.router.navigate(['/account/login'], { queryParams: {} });
  }

  signUp(): void {
    this.router.navigate(['/account/signup'], { queryParams: {} });
  }

  async logOut(): Promise<void> {
    await this.userService.logout();
    this.router.navigate(['/'], { queryParams: {} });
  }

  /*backMenu(): void {
    this.gameMode = null;
    this.singleSide = null;

    this.router.navigate(['/'], { queryParams: {} });
  }*/
}
