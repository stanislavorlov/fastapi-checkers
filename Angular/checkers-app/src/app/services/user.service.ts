import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { BehaviorSubject, firstValueFrom, from, Observable, tap, switchMap, map } from 'rxjs';
import { LocalStorageService } from './local-storage.service';
import { Player } from '../models/player';
import { AccessToken } from '../models/access_token';

@Injectable({
  providedIn: 'root'
})
export class UserService {
  private playerSubject = new BehaviorSubject<Player | null>(null);
  public player$ = this.playerSubject.asObservable();

  constructor(private localStorageService: LocalStorageService, private httpClient: HttpClient) { }

  get currentPlayer(): Player | null {
    return this.playerSubject.value;
  }

  async loadPlayerProfile(): Promise<void> {
    console.log('Loading player profile');
    try {
      const playerData = await firstValueFrom(
        this.httpClient.get<any>('/api/users/me')
      );
      const player = new Player(playerData);
      player.is_guest = playerData.anonymous;
      this.playerSubject.next(player);
    } catch (error) {
      console.log('Error loading profile, likely unauthorized');
      this.playerSubject.next(null);
    }
  }

  async init(): Promise<void> {
    let token = this.localStorageService.getItem(LocalStorageService.JWT_ACCESS_TOKEN);

    if (token) {
      await this.loadPlayerProfile();
    }

    if (!this.currentPlayer) {
      console.log('No valid session found, authenticating as guest');
      const tokenResponse = await firstValueFrom(
        this.httpClient.post<AccessToken>('/api/guest-token', {})
      );
      this.localStorageService.setItem(LocalStorageService.JWT_ACCESS_TOKEN, tokenResponse.access_token);
      await this.loadPlayerProfile();
    }
  }

  authenticateGuest(): Observable<AccessToken> {
    console.log('Authenticating as guest');
    return this.httpClient.post<AccessToken>(
      '/api/guest-token', {}
    ).pipe(
      tap((token) => {
        console.log('Storing guest token in local storage');
        this.localStorageService.setItem(LocalStorageService.JWT_ACCESS_TOKEN, token.access_token);
      })
    );
  }

  authenticate(email: string, password: string): Observable<Player | null> {
    console.log('Authenticating user:', email);
    const body = new URLSearchParams();
    body.set('grant_type', 'password');
    body.set('username', email);
    body.set('password', password);
    body.set('client_id', 'string');
    body.set('client_secret', 'string');

    return this.httpClient.post<AccessToken>(
      '/api/token',
      body.toString(),
      { headers: { 'Content-Type': 'application/x-www-form-urlencoded' } }
    ).pipe(
      tap((token) => {
        this.localStorageService.setItem(LocalStorageService.JWT_ACCESS_TOKEN, token.access_token);
      }),
      switchMap(() => from(this.loadPlayerProfile())),
      map(() => this.currentPlayer)
    );
  }

  register(email: string, password: string, level: string): Observable<any> {
    console.log('Registering user');
    const body = { email, password, level };
    return this.httpClient.post('/api/register', body);
  }

  async logout(): Promise<void> {
    this.localStorageService.removeItem(LocalStorageService.JWT_ACCESS_TOKEN);
    this.playerSubject.next(null);
    await this.init();
  }
}
