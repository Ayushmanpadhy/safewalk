// map/map.component.ts — Main map screen with Leaflet heatmap
import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { MapService } from '../shared/services/map.service';
import { SosService } from '../shared/services/sos.service';
import { StreetScore } from '../shared/models/models';

declare const L: any; // Leaflet loaded via CDN in index.html

@Component({
  selector: 'app-map',
  standalone: true,
  imports: [CommonModule, RouterLink],
  templateUrl: './map.component.html'
})
export class MapComponent implements OnInit, OnDestroy {
  private map: any;
  private markers: any[] = [];
  streets: StreetScore[] = [];
  selectedStreet: StreetScore | null = null;
  loading       = true;
  sosLoading    = false;
  sosSuccess    = false;
  currentHour   = new Date().getHours();
  isNight       = this.currentHour >= 21 || this.currentHour < 6;

  constructor(
    private mapService: MapService,
    private sosService: SosService
  ) {}

  ngOnInit(): void {
    setTimeout(() => {
      this.initMap();
      this.loadHeatmap();
      setInterval(() => this.loadHeatmap(), 600000);
    }, 100);
  }

  private initMap(): void {
    this.map = L.map('safewalk-map', { zoomControl: true }).setView([17.385, 78.4867], 13);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '© OpenStreetMap contributors'
    }).addTo(this.map);

    // Click on map to report
    this.map.on('click', (e: any) => {
      this.selectedStreet = null;
    });
  }

  loadHeatmap(): void {
    this.loading = true;
    this.mapService.getHeatmap().subscribe({
      next: (res) => {
        this.streets = res.streets;
        this.renderMarkers();
        this.loading = false;
      },
      error: () => { this.loading = false; }
    });
  }

  private renderMarkers(): void {
    // Clear old markers
    this.markers.forEach(m => m.remove());
    this.markers = [];

    for (const street of this.streets) {
      const color  = this.mapService.getScoreColor(street.score);
      const radius = 80 + (100 - street.score) * 2; // bigger = more dangerous

      const circle = L.circle([street.lat, street.lng], {
        color,
        fillColor: color,
        fillOpacity: 0.45,
        radius,
        weight: 1
      }).addTo(this.map);

      circle.on('click', () => {
        this.selectedStreet = street;
      });

      this.markers.push(circle);
    }
  }

  centerOnUser(): void {
    navigator.geolocation.getCurrentPosition((pos) => {
      this.map.setView([pos.coords.latitude, pos.coords.longitude], 16);
    });
  }

  triggerSOS(): void {
    this.sosLoading = true;
    navigator.geolocation.getCurrentPosition((pos) => {
      this.sosService.triggerSOS(pos.coords.latitude, pos.coords.longitude).subscribe({
        next: () => {
          this.sosLoading = false;
          this.sosSuccess = true;
          setTimeout(() => this.sosSuccess = false, 5000);
        },
        error: () => { this.sosLoading = false; }
      });
    });
  }

  getScoreLabel(score: number): string {
    return this.mapService.getScoreLabel(score);
  }

  getScoreColor(score: number): string {
    return this.mapService.getScoreColor(score);
  }

  ngOnDestroy(): void {
    if (this.map) this.map.remove();
  }
}
