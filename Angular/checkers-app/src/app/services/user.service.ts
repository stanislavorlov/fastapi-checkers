import { Injectable, inject, PLATFORM_ID } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { BehaviorSubject, firstValueFrom, from, Observable, tap, switchMap, map, catchError, throwError } from 'rxjs';
import { LocalStorageService } from './local-storage.service';
import { Player } from '../models/player';
import { AccessToken } from '../models/access_token';
import { isPlatformBrowser } from '@angular/common';
import { ProfileDto } from '../models/profile-dto';

@Injectable({
  providedIn: 'root'
})
export class UserService {
  private playerSubject = new BehaviorSubject<Player | null>(null);
  public player$ = this.playerSubject.asObservable();
  private platformId = inject(PLATFORM_ID);

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
    if (!isPlatformBrowser(this.platformId)) {
      return;
    }
    let token = this.localStorageService.getItem(LocalStorageService.JWT_ACCESS_TOKEN);

    if (token) {
      await this.loadPlayerProfile();
    }

    if (!this.currentPlayer) {
      console.log('[UserService] No current player. Starting guest authentication.');
      try {
        const tokenResponse = await firstValueFrom(
          this.httpClient.post<AccessToken>('/api/guest-token', {})
        );
        console.log('[UserService] Guest token received. Refresh token exists in response:', !!tokenResponse.refresh_token);

        this.localStorageService.setItem(LocalStorageService.JWT_ACCESS_TOKEN, tokenResponse.access_token);
        this.localStorageService.setItem(LocalStorageService.JWT_REFRESH_TOKEN, tokenResponse.refresh_token);

        const storedRefresh = this.localStorageService.getItem(LocalStorageService.JWT_REFRESH_TOKEN);
        console.log('[UserService] Verification: Refresh token stored in LocalStorage:', !!storedRefresh);

        await this.loadPlayerProfile();
      } catch (err) {
        console.error('[UserService] Guest authentication failed:', err);
      }
    }
  }

  refreshToken(): Observable<AccessToken> {
    const refreshToken = this.localStorageService.getItem(LocalStorageService.JWT_REFRESH_TOKEN);
    console.log('[UserService] refreshToken() called. Refresh token exists:', !!refreshToken);
    if (!refreshToken) {
      return throwError(() => new Error('No refresh token available'));
    }

    return this.httpClient.post<AccessToken>('/api/refresh', { refresh_token: refreshToken }).pipe(
      tap((token) => {
        console.log('[UserService] refreshToken() request successful. Storing new tokens.');
        this.localStorageService.setItem(LocalStorageService.JWT_ACCESS_TOKEN, token.access_token);
        this.localStorageService.setItem(LocalStorageService.JWT_REFRESH_TOKEN, token.refresh_token);
      }),
      catchError(err => {
        console.error('[UserService] refreshToken() request failed:', err);
        return throwError(() => err);
      })
    );
  }

  authenticateGuest(): Observable<AccessToken> {
    console.log('Authenticating as guest');
    return this.httpClient.post<AccessToken>(
      '/api/guest-token', {}
    ).pipe(
      tap((token) => {
        console.log('Storing guest tokens in local storage');
        this.localStorageService.setItem(LocalStorageService.JWT_ACCESS_TOKEN, token.access_token);
        this.localStorageService.setItem(LocalStorageService.JWT_REFRESH_TOKEN, token.refresh_token);
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
        this.localStorageService.setItem(LocalStorageService.JWT_REFRESH_TOKEN, token.refresh_token);
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
    this.localStorageService.removeItem(LocalStorageService.JWT_REFRESH_TOKEN);
    this.playerSubject.next(null);
    // Don't call init() here as it can cause infinite loops if authentication fails.
    // The next navigation or manual login will handle re-initialization.
  }

  getProfile(): Observable<ProfileDto> {
    return this.httpClient.get<ProfileDto>('/api/profile');
  }

  updateProfile(profile: ProfileDto): Observable<any> {
    return this.httpClient.put('/api/profile', profile);
  }
}
