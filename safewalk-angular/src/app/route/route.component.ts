// route/route.component.ts
import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { RouteService } from '../shared/services/route.service';
import { SafeRoute } from '../shared/models/models';
import { MapService } from '../shared/services/map.service';

@Component({
  selector: 'app-route',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink],
  templateUrl: './route.component.html'
})
export class RouteComponent {
  from = { lat: '', lng: '', name: '' };
  to   = { lat: '', lng: '', name: '' };
  result: SafeRoute | null = null;
  loading = false;
  error   = '';

  constructor(private routeService: RouteService, public mapService: MapService) {}

  useMyLocation(target: 'from' | 'to'): void {
    navigator.geolocation.getCurrentPosition((pos) => {
      if (target === 'from') {
        this.from.lat  = pos.coords.latitude.toString();
        this.from.lng  = pos.coords.longitude.toString();
        this.from.name = 'My Location';
      } else {
        this.to.lat  = pos.coords.latitude.toString();
        this.to.lng  = pos.coords.longitude.toString();
        this.to.name = 'My Location';
      }
    });
  }

  planRoute(): void {
    if (!this.from.lat || !this.to.lat) {
      this.error = 'Please enter both start and destination coordinates';
      return;
    }
    this.loading = true;
    this.error   = '';
    this.routeService.getSafeRoute(
      +this.from.lat, +this.from.lng, +this.to.lat, +this.to.lng
    ).subscribe({
      next:  (res) => { this.result = res; this.loading = false; },
      error: (err) => { this.loading = false; this.error = err.error?.error || 'Route planning failed'; }
    });
  }

  getVerdictColor(verdict: string): string {
    return verdict === 'safe' ? '#1D9E75' : verdict === 'moderate' ? '#EF9F27' : '#E24B4A';
  }
}
