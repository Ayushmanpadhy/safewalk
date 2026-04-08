// shared/services/report.service.ts
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
    return this.http.post(`${this.api}/reports`, formData);
  }

  getReports(params?: any): Observable<{ reports: Report[] }> {
    return this.http.get<{ reports: Report[] }>(`${this.api}/reports`, { params });
  }

  getReport(id: number): Observable<{ report: Report }> {
    return this.http.get<{ report: Report }>(`${this.api}/reports/${id}`);
  }

  voteReport(id: number, vote: 'up' | 'down'): Observable<any> {
    return this.http.post(`${this.api}/reports/${id}/vote`, { vote });
  }
}
