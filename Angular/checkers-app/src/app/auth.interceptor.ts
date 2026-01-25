import { HttpInterceptorFn, HttpErrorResponse } from '@angular/common/http';
import { LocalStorageService } from './services/local-storage.service';
import { inject, PLATFORM_ID, Injector } from '@angular/core';
import { isPlatformServer } from '@angular/common';
import { tap, catchError, switchMap, throwError } from 'rxjs';
import { USER_AGENT, requestContext } from './tokens';
import { UserService } from './services/user.service';
import { AccessToken } from './models/access_token';

export const authInterceptor: HttpInterceptorFn = (req, next) => {
  const platformId = inject(PLATFORM_ID);
  const injector = inject(Injector);
  const isServer = isPlatformServer(platformId);
  const localStorage = inject(LocalStorageService);

  const authToken = localStorage.getItem(LocalStorageService.JWT_ACCESS_TOKEN);
  let ssrUserAgent = inject(USER_AGENT, { optional: true });

  if (isServer) {
    const store = requestContext?.getStore?.();
    if (store?.userAgent) {
      ssrUserAgent = store.userAgent;
    }
  }

  console.log(`[AuthInterceptor] Intercepting request: ${req.url}, hasToken: ${!!authToken}`);

  const addTokenHeader = (request: any, token: string | null) => {
    let headers = request.headers;
    if (!!token && !(request.url.includes('/api/token') || request.url.includes('/api/guest-token') || request.url.includes('/api/refresh'))) {
      headers = headers.set('Authorization', `Bearer ${token}`);
    }
    if (isServer) {
      headers = headers.set('X-SSR-Request', 'true');
      if (ssrUserAgent) {
        headers = headers.set('User-Agent', ssrUserAgent);
      }
    }
    return request.clone({ headers });
  };

  return next(addTokenHeader(req, authToken)).pipe(
    catchError((error: HttpErrorResponse) => {
      // If we get a 401 and it's not from a login/refresh request, try to refresh
      // We ONLY refresh on the client (browser) because server has no LocalStorage for tokens
      const refreshToken = localStorage.getItem(LocalStorageService.JWT_REFRESH_TOKEN);

      if (!isServer && error.status === 401 && !!refreshToken && !req.url.includes('/api/token') && !req.url.includes('/api/guest-token') && !req.url.includes('/api/refresh')) {
        console.warn(`[AuthInterceptor] 401 detected for ${req.url}. Attempting to refresh token...`);
        const userService = injector.get(UserService);
        return userService.refreshToken().pipe(
          switchMap((newToken: AccessToken) => {
            console.log(`[AuthInterceptor] Token refreshed successfully. Retrying ${req.url}`);
            return next(addTokenHeader(req, newToken.access_token));
          }),
          catchError((refreshError) => {
            console.error('[AuthInterceptor] Refresh token also failed or expired. Logging out.');
            userService.logout();
            return throwError(() => refreshError);
          })
        );
      }

      // If no refresh token or not eligible for refresh, just logout and let the app re-init
      if (error.status === 401 && !req.url.includes('/api/token') && !req.url.includes('/api/guest-token') && !req.url.includes('/api/refresh')) {
        console.error('[AuthInterceptor] 401 detected but no refresh token found or not eligible. Logging out.');
        const userService = injector.get(UserService);
        userService.logout();
      }

      return throwError(() => error);
    })
  );
};
