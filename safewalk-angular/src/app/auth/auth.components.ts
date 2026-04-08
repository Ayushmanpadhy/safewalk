// src/app/auth/login/login.component.ts
import { Component } from '@angular/core';
import { Router } from '@angular/router';
import { AuthService } from '../../shared/services/auth.service';

@Component({
  selector: 'app-login',
  template: `
    <div class="auth-wrapper">
      <div class="auth-card">
        <div class="auth-logo">
          <span class="logo-dot"></span>
          <h1>SafeWalk</h1>
        </div>
        <p class="auth-sub">Real-time street safety for everyone</p>

        <div class="alert alert-danger" *ngIf="error">{{ error }}</div>

        <form (ngSubmit)="onLogin()">
          <div class="form-group">
            <label>Email</label>
            <input type="email" [(ngModel)]="email" name="email"
                   placeholder="you@email.com" required />
          </div>
          <div class="form-group">
            <label>Password</label>
            <input type="password" [(ngModel)]="password" name="password"
                   placeholder="••••••••" required />
          </div>
          <button type="submit" class="btn-primary" [disabled]="loading">
            {{ loading ? 'Signing in...' : 'Sign In' }}
          </button>
        </form>

        <p class="auth-footer">
          No account? <a routerLink="/register">Register here</a>
        </p>
      </div>
    </div>
  `,
  styles: [`
    .auth-wrapper {
      min-height: 100vh; display: flex;
      align-items: center; justify-content: center;
      background: #f5f5f3;
    }
    .auth-card {
      background: white; border-radius: 16px;
      padding: 2.5rem; width: 100%; max-width: 400px;
      border: 1px solid #e5e5e3;
    }
    .auth-logo { display: flex; align-items: center; gap: 10px; margin-bottom: 4px; }
    .auth-logo h1 { font-size: 22px; font-weight: 600; margin: 0; }
    .logo-dot {
      width: 12px; height: 12px; border-radius: 50%;
      background: #E24B4A; display: inline-block;
    }
    .auth-sub { color: #888; font-size: 14px; margin: 0 0 1.5rem; }
    .form-group { margin-bottom: 1rem; }
    label { display: block; font-size: 13px; font-weight: 500; margin-bottom: 5px; }
    input {
      width: 100%; padding: 10px 12px; border: 1px solid #e0e0de;
      border-radius: 8px; font-size: 14px; box-sizing: border-box;
    }
    input:focus { outline: none; border-color: #378ADD; }
    .btn-primary {
      width: 100%; padding: 11px; background: #E24B4A; color: white;
      border: none; border-radius: 8px; font-size: 14px; font-weight: 500;
      cursor: pointer; margin-top: 8px;
    }
    .btn-primary:hover { background: #c93a39; }
    .btn-primary:disabled { opacity: 0.6; cursor: not-allowed; }
    .auth-footer { text-align: center; font-size: 13px; color: #888; margin-top: 1rem; }
    .auth-footer a { color: #378ADD; text-decoration: none; }
    .alert-danger {
      background: #FCEBEB; color: #791F1F; padding: 10px 12px;
      border-radius: 8px; font-size: 13px; margin-bottom: 1rem;
    }
  `]
})
export class LoginComponent {
  email    = '';
  password = '';
  loading  = false;
  error    = '';

  constructor(private auth: AuthService, private router: Router) {}

  onLogin(): void {
    this.loading = true;
    this.error   = '';
    this.auth.login({ email: this.email, password: this.password }).subscribe({
      next: (res) => {
        this.loading = false;
        // Redirect based on role
        this.router.navigate([res.user.role === 'user' ? '/map' : '/admin']);
      },
      error: (err) => {
        this.loading = false;
        this.error   = err.error?.error || 'Login failed';
      }
    });
  }
}


// src/app/auth/register/register.component.ts
import { Component } from '@angular/core';
import { Router } from '@angular/router';
import { AuthService } from '../../shared/services/auth.service';

@Component({
  selector: 'app-register',
  template: `
    <div class="auth-wrapper">
      <div class="auth-card">
        <div class="auth-logo">
          <span class="logo-dot"></span>
          <h1>SafeWalk</h1>
        </div>
        <p class="auth-sub">Create your account</p>

        <div class="alert alert-danger" *ngIf="error">{{ error }}</div>

        <form (ngSubmit)="onRegister()">
          <div class="form-group">
            <label>Full Name</label>
            <input type="text" [(ngModel)]="name" name="name" placeholder="Your name" required />
          </div>
          <div class="form-group">
            <label>Email</label>
            <input type="email" [(ngModel)]="email" name="email" placeholder="you@email.com" required />
          </div>
          <div class="form-group">
            <label>Phone (optional)</label>
            <input type="tel" [(ngModel)]="phone" name="phone" placeholder="+91 9999999999" />
          </div>
          <div class="form-group">
            <label>Password</label>
            <input type="password" [(ngModel)]="password" name="password" placeholder="Min 6 characters" required />
          </div>
          <button type="submit" class="btn-primary" [disabled]="loading">
            {{ loading ? 'Creating account...' : 'Create Account' }}
          </button>
        </form>

        <p class="auth-footer">
          Already registered? <a routerLink="/login">Sign in</a>
        </p>
      </div>
    </div>
  `,
  styles: [`
    .auth-wrapper { min-height:100vh; display:flex; align-items:center; justify-content:center; background:#f5f5f3; }
    .auth-card { background:white; border-radius:16px; padding:2.5rem; width:100%; max-width:400px; border:1px solid #e5e5e3; }
    .auth-logo { display:flex; align-items:center; gap:10px; margin-bottom:4px; }
    .auth-logo h1 { font-size:22px; font-weight:600; margin:0; }
    .logo-dot { width:12px; height:12px; border-radius:50%; background:#E24B4A; display:inline-block; }
    .auth-sub { color:#888; font-size:14px; margin:0 0 1.5rem; }
    .form-group { margin-bottom:1rem; }
    label { display:block; font-size:13px; font-weight:500; margin-bottom:5px; }
    input { width:100%; padding:10px 12px; border:1px solid #e0e0de; border-radius:8px; font-size:14px; box-sizing:border-box; }
    input:focus { outline:none; border-color:#378ADD; }
    .btn-primary { width:100%; padding:11px; background:#E24B4A; color:white; border:none; border-radius:8px; font-size:14px; font-weight:500; cursor:pointer; margin-top:8px; }
    .btn-primary:hover { background:#c93a39; }
    .btn-primary:disabled { opacity:0.6; cursor:not-allowed; }
    .auth-footer { text-align:center; font-size:13px; color:#888; margin-top:1rem; }
    .auth-footer a { color:#378ADD; text-decoration:none; }
    .alert-danger { background:#FCEBEB; color:#791F1F; padding:10px 12px; border-radius:8px; font-size:13px; margin-bottom:1rem; }
  `]
})
export class RegisterComponent {
  name     = '';
  email    = '';
  password = '';
  phone    = '';
  loading  = false;
  error    = '';

  constructor(private auth: AuthService, private router: Router) {}

  onRegister(): void {
    this.loading = true;
    this.error   = '';
    this.auth.register({ name: this.name, email: this.email, password: this.password, phone: this.phone })
      .subscribe({
        next: () => { this.loading = false; this.router.navigate(['/map']); },
        error: (err) => { this.loading = false; this.error = err.error?.error || 'Registration failed'; }
      });
  }
}
