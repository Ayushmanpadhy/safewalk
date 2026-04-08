// shared/services/admin.service.ts
import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';

@Injectable({ providedIn: 'root' })
export class AdminService {
  private api = environment.apiUrl;

  constructor(private http: HttpClient) {}

  getAllReports(params?: any): Observable<any> {
    return this.http.get(`${this.api}/admin/reports`, { params });
  }

  resolveReport(id: number): Observable<any> {
    return this.http.patch(`${this.api}/admin/reports/${id}/resolve`, {});
  }

  getHotspots(): Observable<any> {
    return this.http.get(`${this.api}/admin/hotspots`);
  }

  getAnalytics(): Observable<any> {
    return this.http.get(`${this.api}/admin/analytics`);
  }

  verifyUser(id: number): Observable<any> {
    return this.http.patch(`${this.api}/admin/users/${id}/verify`, {});
  }
}
