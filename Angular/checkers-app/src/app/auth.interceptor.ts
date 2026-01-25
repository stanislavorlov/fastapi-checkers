import { HttpInterceptorFn } from '@angular/common/http';
import { LocalStorageService } from './services/local-storage.service';
import { inject, PLATFORM_ID, Optional } from '@angular/core';
import { isPlatformServer } from '@angular/common';
import { tap } from 'rxjs';
import { USER_AGENT, requestContext } from './tokens';

export const authInterceptor: HttpInterceptorFn = (req, next) => {
  const platformId = inject(PLATFORM_ID);
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

  let headers = req.headers;

  if (!!authToken && !(req.url.includes('/api/token') || req.url.includes('/api/guest-token'))) {
    headers = headers.set('Authorization', `Bearer ${authToken}`);
  }

  // If on server, we forward the original User-Agent
  if (isServer) {
    headers = headers.set('X-SSR-Request', 'true');
    if (ssrUserAgent) {
      headers = headers.set('User-Agent', ssrUserAgent);
    }
  }

  const newReq = req.clone({ headers });

  return next(newReq).pipe(tap(event => {
    // console.log('Event:', event);
  }));
};
