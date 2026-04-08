import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';

@Injectable({ providedIn: 'root' })
export class ApiService {
  private api = environment.apiUrl;
  constructor(private http: HttpClient) {}

  getReports(f?: any): Observable<any> {
    let p = new HttpParams();
    if (f) Object.keys(f).forEach(k => p = p.set(k, f[k]));
    return this.http.get(`${this.api}/reports`, { params: p });
  }
  submitReport(fd: FormData): Observable<any> { return this.http.post(`${this.api}/reports`, fd); }
  voteReport(id: number, vote: string): Observable<any> { return this.http.post(`${this.api}/reports/${id}/vote`, { vote }); }

  getHeatmap(): Observable<any> { return this.http.get(`${this.api}/scores/heatmap`); }
  getStreetScore(id: string): Observable<any> { return this.http.get(`${this.api}/scores/${id}`); }
  getNearbyScores(lat: number, lng: number, r=500): Observable<any> {
    return this.http.get(`${this.api}/scores/nearby`, { params: { lat: `${lat}`, lng: `${lng}`, radius: `${r}` } });
  }

  getSafeRoute(fLat: number, fLng: number, tLat: number, tLng: number): Observable<any> {
    return this.http.get(`${this.api}/route`, { params: { from_lat:`${fLat}`, from_lng:`${fLng}`, to_lat:`${tLat}`, to_lng:`${tLng}` } });
  }
  getRouteHistory(): Observable<any> { return this.http.get(`${this.api}/route/history`); }

  triggerSOS(lat: number, lng: number, address?: string): Observable<any> {
    return this.http.post(`${this.api}/sos`, { lat, lng, address });
  }

  getAdminReports(f?: any): Observable<any> {
    let p = new HttpParams();
    if (f) Object.keys(f).forEach(k => p = p.set(k, f[k]));
    return this.http.get(`${this.api}/admin/reports`, { params: p });
  }
  resolveReport(id: number): Observable<any> { return this.http.patch(`${this.api}/admin/reports/${id}/resolve`, {}); }
  getHotspots(): Observable<any> { return this.http.get(`${this.api}/admin/hotspots`); }
  getAnalytics(): Observable<any> { return this.http.get(`${this.api}/admin/analytics`); }
  verifyUser(id: number): Observable<any> { return this.http.patch(`${this.api}/admin/users/${id}/verify`, {}); }
}
