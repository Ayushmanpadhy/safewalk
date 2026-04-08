// shared/services/auth.service.ts
import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Router } from '@angular/router';
import { BehaviorSubject, Observable, tap } from 'rxjs';
import { environment } from '../../../environments/environment';
import { User, EmergencyContact } from '../models/models';

@Injectable({ providedIn: 'root' })
export class AuthService {
  private api = environment.apiUrl;
  private currentUserSubject = new BehaviorSubject<User | null>(this.loadUser());
  currentUser$ = this.currentUserSubject.asObservable();

  constructor(private http: HttpClient, private router: Router) {}

  private loadUser(): User | null {
    const stored = localStorage.getItem('sw_user');
    return stored ? JSON.parse(stored) : null;
  }

  get currentUser(): User | null {
    return this.currentUserSubject.value;
  }

  get token(): string | null {
    return localStorage.getItem('sw_token');
  }

  get isLoggedIn(): boolean {
    return !!this.token;
  }

  get isAuthority(): boolean {
    return ['authority', 'admin'].includes(this.currentUser?.role || '');
  }

  register(payload: { name: string; email: string; password: string; phone?: string }): Observable<any> {
    return this.http.post(`${this.api}/auth/register`, payload).pipe(
      tap((res: any) => this.storeSession(res))
    );
  }

  login(email: string, password: string): Observable<any> {
    return this.http.post(`${this.api}/auth/login`, { email, password }).pipe(
      tap((res: any) => this.storeSession(res))
    );
  }

  private storeSession(res: any): void {
    localStorage.setItem('sw_token', res.token);
    localStorage.setItem('sw_user', JSON.stringify(res.user));
    this.currentUserSubject.next(res.user);
  }

  logout(): void {
    localStorage.removeItem('sw_token');
    localStorage.removeItem('sw_user');
    this.currentUserSubject.next(null);
    this.router.navigate(['/login']);
  }

  updateEmergencyContacts(contacts: EmergencyContact[]): Observable<any> {
    return this.http.put(`${this.api}/auth/emergency-contacts`, { contacts });
  }
}
