import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { ReactiveFormsModule, FormsModule } from '@angular/forms';
import { HttpClientModule, HTTP_INTERCEPTORS } from '@angular/common/http';
import { RouterModule, Routes } from '@angular/router';
import { CommonModule } from '@angular/common';

import { AppComponent }       from './app.component';
import { LoginComponent }     from './auth/login/login.component';
import { RegisterComponent }  from './auth/register/register.component';
import { MapComponent }       from './map/map.component';
import { ReportComponent }    from './report/report.component';
import { RouteComponent }     from './route/route.component';
import { AdminComponent }     from './admin/admin.component';

import { authGuard, authorityGuard } from './shared/guards/auth.guard';
import { AuthInterceptor }           from './shared/services/auth.interceptor';

const routes: Routes = [
  { path: '',         redirectTo: 'map', pathMatch: 'full' },
  { path: 'login',    component: LoginComponent },
  { path: 'register', component: RegisterComponent },
  { path: 'map',      component: MapComponent,    canActivate: [authGuard] },
  { path: 'report',   component: ReportComponent, canActivate: [authGuard] },
  { path: 'route',    component: RouteComponent,  canActivate: [authGuard] },
  { path: 'admin',    component: AdminComponent,  canActivate: [authGuard, authorityGuard] },
  { path: '**',       redirectTo: 'map' }
];

@NgModule({
  declarations: [],
  imports: [
    BrowserModule, CommonModule, ReactiveFormsModule, FormsModule,
    HttpClientModule, RouterModule.forRoot(routes),
    AppComponent, LoginComponent, RegisterComponent,
    MapComponent, ReportComponent, RouteComponent, AdminComponent
  ],
  providers: [
    { provide: HTTP_INTERCEPTORS, useClass: AuthInterceptor, multi: true }
  ],
  bootstrap: [AppComponent]
})
export class AppModule {}
