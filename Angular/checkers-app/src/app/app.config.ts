import { ApplicationConfig, inject, provideAppInitializer, provideZoneChangeDetection } from '@angular/core';
import { provideRouter } from '@angular/router';
import { routes } from './app.routes';
import { provideClientHydration, withEventReplay } from '@angular/platform-browser';
import { provideHttpClient, withFetch, withInterceptors, withInterceptorsFromDi } from '@angular/common/http';
import { authInterceptor } from './auth.interceptor';
import { UserService } from './services/user.service';

export const appConfig: ApplicationConfig = {
  providers: [
    provideZoneChangeDetection({ eventCoalescing: true }), 
    provideRouter(routes), 
    provideHttpClient(
      withInterceptors([
        authInterceptor,
      ]),
      withInterceptorsFromDi(),
      withFetch()
    ),
    provideAppInitializer(async () => {
      // ToDo: create guest token during game creation if not authenticated
      const userService = inject(UserService);
      await userService.init();
    }),
    provideClientHydration(withEventReplay())
  ]
};
