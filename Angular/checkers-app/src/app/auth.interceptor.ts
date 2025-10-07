import { HttpInterceptorFn } from '@angular/common/http';
import { LocalStorageService } from './services/local-storage.service';
import { inject } from '@angular/core';
import { tap } from 'rxjs';

export const authInterceptor: HttpInterceptorFn = (req, next) => {
  const authToken = inject(LocalStorageService).getItem(LocalStorageService.JWT_ACCESS_TOKEN);

  if (!!authToken) {
    const newReq = req.clone({
      setHeaders: {
        Authorization: authToken ? `Bearer ${authToken}` : '',
      }
    });
    return next(newReq).pipe(tap(event => {
      // console.log('Event:', event);
    }));
  } else {
    return next(req).pipe(tap(event => {
      // console.log('Event:', event);
    }));
  }
};
