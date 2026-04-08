// src/app/shared/services/map.service.ts
import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';
import { StreetScore, SafeRoute } from '../models/models';

@Injectable({ providedIn: 'root' })
export class MapService {
  private api = environment.apiUrl;
  constructor(private http: HttpClient) {}

  getHeatmap(): Observable<{ streets: StreetScore[] }> {
    return this.http.get<any>(`${this.api}/scores/heatmap`);
  }

  getStreetScore(streetId: string): Observable<any> {
    return this.http.get<any>(`${this.api}/scores/${streetId}`);
  }

  getNearbyScores(lat: number, lng: number, radius = 500): Observable<any> {
    return this.http.get<any>(`${this.api}/scores/nearby?lat=${lat}&lng=${lng}&radius=${radius}`);
  }

  getSafeRoute(fromLat: number, fromLng: number, toLat: number, toLng: number): Observable<SafeRoute> {
    return this.http.get<SafeRoute>(
      `${this.api}/route?from_lat=${fromLat}&from_lng=${fromLng}&to_lat=${toLat}&to_lng=${toLng}`
    );
  }

  getRouteHistory(): Observable<any> {
    return this.http.get<any>(`${this.api}/route/history`);
  }
}


// src/app/shared/services/report.service.ts
import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';
import { Report } from '../models/models';

@Injectable({ providedIn: 'root' })
export class ReportService {
  private api = environment.apiUrl;
  constructor(private http: HttpClient) {}

  submitReport(formData: FormData): Observable<any> {
    return this.http.post<any>(`${this.api}/reports`, formData);
  }

  getReports(filters?: any): Observable<{ reports: Report[] }> {
    let params = '';
    if (filters) {
      const q = new URLSearchParams(filters);
      params = '?' + q.toString();
    }
    return this.http.get<any>(`${this.api}/reports${params}`);
  }

  getReport(id: number): Observable<{ report: Report }> {
    return this.http.get<any>(`${this.api}/reports/${id}`);
  }

  voteReport(id: number, vote: 'up' | 'down'): Observable<any> {
    return this.http.post<any>(`${this.api}/reports/${id}/vote`, { vote });
  }
}


// src/app/shared/services/sos.service.ts
import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';

@Injectable({ providedIn: 'root' })
export class SosService {
  private api = environment.apiUrl;
  constructor(private http: HttpClient) {}

  triggerSOS(lat: number, lng: number, address?: string): Observable<any> {
    return this.http.post<any>(`${this.api}/sos`, { lat, lng, address });
  }

  getHistory(): Observable<any> {
    return this.http.get<any>(`${this.api}/sos/history`);
  }
}


// src/app/shared/services/admin.service.ts
import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';

@Injectable({ providedIn: 'root' })
export class AdminService {
  private api = environment.apiUrl;
  constructor(private http: HttpClient) {}

  getReports(filters?: any): Observable<any> {
    const params = filters ? '?' + new URLSearchParams(filters).toString() : '';
    return this.http.get<any>(`${this.api}/admin/reports${params}`);
  }

  resolveReport(id: number): Observable<any> {
    return this.http.patch<any>(`${this.api}/admin/reports/${id}/resolve`, {});
  }

  getHotspots(): Observable<any> {
    return this.http.get<any>(`${this.api}/admin/hotspots`);
  }

  getAnalytics(): Observable<any> {
    return this.http.get<any>(`${this.api}/admin/analytics`);
  }

  verifyUser(id: number): Observable<any> {
    return this.http.patch<any>(`${this.api}/admin/users/${id}/verify`, {});
  }
}
