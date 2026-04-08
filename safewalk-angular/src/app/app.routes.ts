// app.routes.ts
import { Routes } from '@angular/router';
import { authGuard, authorityGuard } from './shared/guards/auth.guard';

export const routes: Routes = [
  { path: '',         redirectTo: '/map', pathMatch: 'full' },
  { path: 'login',    loadComponent: () => import('./auth/login/login.component').then(m => m.LoginComponent) },
  { path: 'register', loadComponent: () => import('./auth/register/register.component').then(m => m.RegisterComponent) },
  { path: 'map',      loadComponent: () => import('./map/map.component').then(m => m.MapComponent), canActivate: [authGuard] },
  { path: 'report',   loadComponent: () => import('./report/report.component').then(m => m.ReportComponent), canActivate: [authGuard] },
  { path: 'route',    loadComponent: () => import('./route/route.component').then(m => m.RouteComponent), canActivate: [authGuard] },
  { path: 'admin',    loadComponent: () => import('./admin/admin.component').then(m => m.AdminComponent), canActivate: [authGuard, authorityGuard] },
  { path: '**',       redirectTo: '/map' }
];
