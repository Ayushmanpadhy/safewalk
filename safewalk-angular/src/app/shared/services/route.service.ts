// shared/services/route.service.ts
import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';
import { SafeRoute } from '../models/models';

@Injectable({ providedIn: 'root' })
export class RouteService {
  private api = environment.apiUrl;

  constructor(private http: HttpClient) {}

  getSafeRoute(fromLat: number, fromLng: number, toLat: number, toLng: number): Observable<SafeRoute> {
    return this.http.get<SafeRoute>(
      `${this.api}/route?from_lat=${fromLat}&from_lng=${fromLng}&to_lat=${toLat}&to_lng=${toLng}`
    );
  }

  getRouteHistory(): Observable<any> {
    return this.http.get(`${this.api}/route/history`);
  }
}
