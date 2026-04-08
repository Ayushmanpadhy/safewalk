// shared/services/map.service.ts
import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';
import { StreetScore } from '../models/models';

@Injectable({ providedIn: 'root' })
export class MapService {
  private api = environment.apiUrl;

  constructor(private http: HttpClient) {}

  getHeatmap(): Observable<{ streets: StreetScore[] }> {
    return this.http.get<{ streets: StreetScore[] }>(`${this.api}/scores/heatmap`);
  }

  getStreetScore(streetId: string): Observable<any> {
    return this.http.get(`${this.api}/scores/${streetId}`);
  }

  getNearbyScores(lat: number, lng: number, radius = 500): Observable<any> {
    return this.http.get(`${this.api}/scores/nearby?lat=${lat}&lng=${lng}&radius=${radius}`);
  }

  // Returns color hex based on score
  getScoreColor(score: number): string {
    if (score >= 80) return '#1D9E75'; // green  — safe
    if (score >= 55) return '#EF9F27'; // amber  — moderate
    if (score >= 30) return '#D85A30'; // orange — caution
    return '#E24B4A';                  // red    — danger
  }

  // Returns label based on score
  getScoreLabel(score: number): string {
    if (score >= 80) return 'Very Safe';
    if (score >= 55) return 'Moderate';
    if (score >= 30) return 'Caution';
    return 'Danger Zone';
  }
}
