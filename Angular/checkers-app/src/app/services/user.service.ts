import { Injectable } from '@angular/core';
import { LocalStorageService } from './local-storage.service';
import { HttpClient } from '@angular/common/http';
import { BehaviorSubject, firstValueFrom, Observable, tap } from 'rxjs';
import { Player } from '../models/player';
import { AccessToken } from '../models/access_token';
import { PlayerId } from '../models/player-id';

@Injectable({
  providedIn: 'root'
})
export class UserService {
  private playerSubject = new BehaviorSubject<Player | null>(null);
  public player$ = this.playerSubject.asObservable();

  constructor(private localStorageService: LocalStorageService, private httpClient: HttpClient) {
    
  }

  get currentPlayer(): Player | null {
    return this.playerSubject.value;
  }

  async loadPlayerProfile(): Promise<void> {
    try {
      const player = await firstValueFrom(
        this.httpClient.get<Player>('/api/users/me')
      );
      this.playerSubject.next(player);
    } catch (error) {
      console.log('401 Unauthorized, using guest profile');
      this.playerSubject.next(this.createGuestPlayer());
    }
  }

  authenticate(email: string, password: string): Observable<AccessToken> {
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
      })
    );
  }

  register(email: string, password: string): Observable<any> {
    console.log('Registering user');

    const body = {
      email: email,
      password: password
    };

    return this.httpClient.post('/api/register', body);
  }

  logout(): void {
    this.localStorageService.removeItem(LocalStorageService.JWT_ACCESS_TOKEN);
  }

  private createGuestPlayer(): Player {
    const id = Date.now().toString();

    return { player_id: PlayerId.generate().id, username: `Guest${id}`, first_name: '', last_name: '', country: '' };
  }
}
