// shared/services/sos.service.ts
import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';

@Injectable({ providedIn: 'root' })
export class SosService {
  private api = environment.apiUrl;

  constructor(private http: HttpClient) {}

  triggerSOS(lat: number, lng: number, address?: string): Observable<any> {
    return this.http.post(`${this.api}/sos`, { lat, lng, address });
  }

  getSOSHistory(): Observable<any> {
    return this.http.get(`${this.api}/sos/history`);
  }
}
