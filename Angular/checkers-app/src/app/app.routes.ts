import { Routes } from '@angular/router';

export const routes: Routes = [
    { path: '', loadComponent: () => import('./start-page/start-page.component').then(m => m.StartComponent) },
    { path: 'game', loadComponent: () => import('./choose-game/choose-game.component').then(m => m.GameComponent) },
    { path: 'account/login', loadComponent: () => import('./account/login/login.component').then(m => m.LoginComponent) },
    { path: 'account/signup', loadComponent: () => import('./account/signup/signup.component').then(m => m.SignupComponent) },
    { path: ':id', loadComponent: () => import('./play/play.component').then(m => m.PlayComponent) }
];
