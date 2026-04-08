// auth/register/register.component.ts
import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { AuthService } from '../../shared/services/auth.service';

@Component({
  selector: 'app-register',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink],
  templateUrl: './register.component.html'
})
export class RegisterComponent {
  form = { name: '', email: '', password: '', phone: '' };
  loading = false;
  error   = '';

  constructor(private auth: AuthService, private router: Router) {}

  onSubmit(): void {
    this.loading = true;
    this.error   = '';
    this.auth.register(this.form).subscribe({
      next: () => { this.loading = false; this.router.navigate(['/map']); },
      error: (err) => { this.loading = false; this.error = err.error?.error || 'Registration failed'; }
    });
  }
}
