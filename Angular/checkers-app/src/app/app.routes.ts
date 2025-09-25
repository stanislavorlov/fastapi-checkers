import { Routes } from '@angular/router';

export const routes: Routes = [
    { path: '', loadComponent: () => import('./start/start.component').then(m => m.StartComponent) },
    { path: ':id', loadComponent: () => import('./play/play.component').then(m => m.PlayComponent) }
];
