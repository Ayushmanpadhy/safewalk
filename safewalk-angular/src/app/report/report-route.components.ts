// src/app/report/report.component.ts
import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { ReportService } from '../shared/services/services';
import { INCIDENT_TYPES } from '../shared/models/models';

@Component({
  selector: 'app-report',
  template: `
    <div class="page-wrapper">
      <div class="page-card">
        <div class="page-header">
          <a routerLink="/map" class="back-link">← Back to Map</a>
          <h2>Report an Incident</h2>
          <p>Your report helps keep the community safe. GPS location auto-fills.</p>
        </div>

        <div class="alert alert-success" *ngIf="success">
          Report submitted! The safety score will update in the next cycle.
        </div>
        <div class="alert alert-danger" *ngIf="error">{{ error }}</div>

        <form (ngSubmit)="onSubmit()">
          <div class="form-group">
            <label>Location (street name)</label>
            <input type="text" [(ngModel)]="streetName" name="streetName"
                   placeholder="e.g. MG Road near Metro Station" required />
          </div>

          <div class="form-group">
            <label>GPS Coordinates</label>
            <div class="gps-row">
              <input type="number" [(ngModel)]="lat" name="lat" placeholder="Latitude" step="any" required />
              <input type="number" [(ngModel)]="lng" name="lng" placeholder="Longitude" step="any" required />
              <button type="button" class="btn-gps" (click)="getGPS()">Use GPS</button>
            </div>
          </div>

          <div class="form-group">
            <label>Incident Type</label>
            <div class="incident-grid">
              <div *ngFor="let type of incidentTypes"
                   class="incident-chip"
                   [class.selected]="incidentType === type.value"
                   (click)="incidentType = type.value">
                <span class="chip-label">{{ type.label }}</span>
                <span class="chip-sev sev-{{ type.severity }}">Severity {{ type.severity }}</span>
              </div>
            </div>
          </div>

          <div class="form-group">
            <label>Description (optional)</label>
            <textarea [(ngModel)]="description" name="description" rows="3"
                      placeholder="What happened? Any extra details..."></textarea>
          </div>

          <div class="form-group">
            <label>Photo Evidence (optional)</label>
            <input type="file" (change)="onFileSelect($event)" accept="image/*" />
          </div>

          <div class="form-check">
            <input type="checkbox" [(ngModel)]="anonymous" name="anonymous" id="anon" />
            <label for="anon">Submit anonymously</label>
          </div>

          <button type="submit" class="btn-primary" [disabled]="loading || !incidentType">
            {{ loading ? 'Submitting...' : 'Submit Report' }}
          </button>
        </form>
      </div>
    </div>
  `,
  styles: [`
    .page-wrapper { min-height:100vh; background:#f5f5f3; padding:2rem 1rem; }
    .page-card { max-width:600px; margin:0 auto; background:white; border-radius:16px; padding:2rem; border:1px solid #e5e5e3; }
    .back-link { font-size:13px; color:#378ADD; text-decoration:none; }
    h2 { font-size:20px; font-weight:600; margin:8px 0 4px; }
    p  { color:#888; font-size:14px; margin:0 0 1.5rem; }
    .form-group { margin-bottom:1.25rem; }
    label { display:block; font-size:13px; font-weight:500; margin-bottom:6px; }
    input, textarea {
      width:100%; padding:10px 12px; border:1px solid #e0e0de;
      border-radius:8px; font-size:14px; box-sizing:border-box; font-family:inherit;
    }
    input:focus, textarea:focus { outline:none; border-color:#378ADD; }
    .gps-row { display:flex; gap:8px; }
    .gps-row input { flex:1; }
    .btn-gps { padding:10px 14px; background:#E1F5EE; color:#085041; border:none; border-radius:8px; font-size:13px; cursor:pointer; white-space:nowrap; }
    .incident-grid { display:grid; grid-template-columns:1fr 1fr; gap:8px; }
    .incident-chip {
      border:1px solid #e5e5e3; border-radius:8px; padding:10px 12px;
      cursor:pointer; transition:all 0.15s;
    }
    .incident-chip:hover   { border-color:#aaa; }
    .incident-chip.selected { border-color:#E24B4A; background:#FCEBEB; }
    .chip-label { display:block; font-size:13px; font-weight:500; }
    .chip-sev   { display:block; font-size:11px; color:#888; margin-top:2px; }
    .sev-5 { color:#E24B4A !important; }
    .sev-4 { color:#D85A30 !important; }
    .sev-3 { color:#EF9F27 !important; }
    .form-check { display:flex; align-items:center; gap:8px; margin-bottom:1.25rem; }
    .form-check input { width:auto; }
    .form-check label { margin:0; font-size:14px; }
    .btn-primary { width:100%; padding:12px; background:#E24B4A; color:white; border:none; border-radius:8px; font-size:15px; font-weight:500; cursor:pointer; }
    .btn-primary:disabled { opacity:0.6; cursor:not-allowed; }
    .alert-success { background:#E1F5EE; color:#085041; padding:10px 14px; border-radius:8px; font-size:13px; margin-bottom:1rem; }
    .alert-danger  { background:#FCEBEB; color:#791F1F; padding:10px 14px; border-radius:8px; font-size:13px; margin-bottom:1rem; }
  `]
})
export class ReportComponent implements OnInit {
  streetName   = '';
  lat          = 0;
  lng          = 0;
  incidentType = '';
  description  = '';
  anonymous    = false;
  photoFile:   File | null = null;
  loading      = false;
  success      = false;
  error        = '';

  incidentTypes = INCIDENT_TYPES;

  constructor(
    private reportSvc: ReportService,
    private route: ActivatedRoute,
    private router: Router
  ) {}

  ngOnInit(): void {
    // Pre-fill from query params (e.g. from map click)
    this.route.queryParams.subscribe(p => {
      if (p['lat'])    this.lat        = parseFloat(p['lat']);
      if (p['lng'])    this.lng        = parseFloat(p['lng']);
      if (p['street']) this.streetName = p['street'];
    });
  }

  getGPS(): void {
    navigator.geolocation.getCurrentPosition(pos => {
      this.lat = pos.coords.latitude;
      this.lng = pos.coords.longitude;
    });
  }

  onFileSelect(evt: Event): void {
    const input = evt.target as HTMLInputElement;
    if (input.files?.length) this.photoFile = input.files[0];
  }

  onSubmit(): void {
    this.loading = true;
    this.error   = '';
    this.success = false;

    const fd = new FormData();
    fd.append('lat',           String(this.lat));
    fd.append('lng',           String(this.lng));
    fd.append('street_name',   this.streetName);
    fd.append('incident_type', this.incidentType);
    fd.append('description',   this.description);
    fd.append('anonymous',     String(this.anonymous));
    if (this.photoFile) fd.append('photo', this.photoFile);

    this.reportSvc.submitReport(fd).subscribe({
      next: () => {
        this.loading = false;
        this.success = true;
        setTimeout(() => this.router.navigate(['/map']), 2500);
      },
      error: (err) => {
        this.loading = false;
        this.error   = err.error?.error || 'Submission failed';
      }
    });
  }
}


// src/app/route/route.component.ts
import { Component } from '@angular/core';
import { MapService } from '../shared/services/services';
import { SafeRoute, scoreToColor, scoreToLabel } from '../shared/models/models';

@Component({
  selector: 'app-route',
  template: `
    <div class="page-wrapper">
      <div class="page-card">
        <a routerLink="/map" class="back-link">← Back to Map</a>
        <h2>Plan a Safe Route</h2>
        <p>The route planner avoids streets with safety score below 40.</p>

        <div class="form-row">
          <div class="form-group">
            <label>From (latitude)</label>
            <input type="number" [(ngModel)]="fromLat" placeholder="17.3850" step="any" />
          </div>
          <div class="form-group">
            <label>From (longitude)</label>
            <input type="number" [(ngModel)]="fromLng" placeholder="78.4867" step="any" />
          </div>
        </div>
        <div class="form-row">
          <div class="form-group">
            <label>To (latitude)</label>
            <input type="number" [(ngModel)]="toLat" placeholder="17.4200" step="any" />
          </div>
          <div class="form-group">
            <label>To (longitude)</label>
            <input type="number" [(ngModel)]="toLng" placeholder="78.5100" step="any" />
          </div>
        </div>
        <button class="btn-gps" (click)="fillCurrentLocation()">Use my current location as start</button>
        <button class="btn-primary" (click)="planRoute()" [disabled]="loading">
          {{ loading ? 'Finding safe route...' : 'Find Safe Route' }}
        </button>

        <!-- Result -->
        <div class="result-card" *ngIf="route">
          <div class="result-header">
            <span class="verdict" [class]="route.safety_verdict">
              {{ route.safety_verdict | titlecase }}
            </span>
            <span class="avg-score" [style.color]="scoreToColor(route.avg_score)">
              Avg score: {{ route.avg_score }}
            </span>
          </div>
          <p class="result-sub">{{ route.waypoints.length }} waypoints &bull; {{ route.direct_dist_m }}m approx distance</p>

          <div class="waypoints">
            <div *ngFor="let wp of route.waypoints; let i = index" class="waypoint">
              <span class="wp-num">{{ i + 1 }}</span>
              <span class="wp-coords">{{ wp.lat | number:'1.4-4' }}, {{ wp.lng | number:'1.4-4' }}</span>
              <span class="wp-score" *ngIf="wp.score" [style.color]="scoreToColor(wp.score)">
                {{ wp.score }}
              </span>
            </div>
          </div>

          <div class="danger-list" *ngIf="route.danger_streets.length">
            <p class="danger-title">Streets being avoided:</p>
            <div *ngFor="let d of route.danger_streets" class="danger-item">
              {{ d.street_name }} — score {{ d.score }}
            </div>
          </div>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .page-wrapper { min-height:100vh; background:#f5f5f3; padding:2rem 1rem; }
    .page-card { max-width:600px; margin:0 auto; background:white; border-radius:16px; padding:2rem; border:1px solid #e5e5e3; }
    .back-link { font-size:13px; color:#378ADD; text-decoration:none; }
    h2 { font-size:20px; font-weight:600; margin:8px 0 4px; }
    p  { color:#888; font-size:14px; margin:0 0 1rem; }
    .form-row { display:grid; grid-template-columns:1fr 1fr; gap:12px; }
    .form-group { margin-bottom:1rem; }
    label { display:block; font-size:13px; font-weight:500; margin-bottom:5px; }
    input { width:100%; padding:10px 12px; border:1px solid #e0e0de; border-radius:8px; font-size:14px; box-sizing:border-box; }
    .btn-gps { background:#E1F5EE; color:#085041; border:none; border-radius:8px; padding:9px 16px; font-size:13px; cursor:pointer; margin-bottom:12px; display:block; }
    .btn-primary { width:100%; padding:12px; background:#E24B4A; color:white; border:none; border-radius:8px; font-size:15px; font-weight:500; cursor:pointer; margin-bottom:1.5rem; }
    .btn-primary:disabled { opacity:0.6; }
    .result-card { background:#f9f9f7; border-radius:12px; padding:1rem; border:1px solid #e5e5e3; }
    .result-header { display:flex; justify-content:space-between; align-items:center; margin-bottom:6px; }
    .verdict { font-size:14px; font-weight:600; padding:4px 12px; border-radius:20px; }
    .verdict.safe      { background:#E1F5EE; color:#085041; }
    .verdict.moderate  { background:#FAEEDA; color:#633806; }
    .verdict.dangerous { background:#FCEBEB; color:#791F1F; }
    .avg-score { font-size:14px; font-weight:600; }
    .result-sub { font-size:12px; color:#888; margin:0 0 12px; }
    .waypoints { display:flex; flex-direction:column; gap:5px; margin-bottom:12px; }
    .waypoint { display:flex; align-items:center; gap:8px; font-size:13px; }
    .wp-num { width:22px; height:22px; border-radius:50%; background:#e5e5e3; display:flex; align-items:center; justify-content:center; font-size:11px; font-weight:600; flex-shrink:0; }
    .wp-coords { flex:1; color:#555; font-family:monospace; font-size:12px; }
    .wp-score { font-weight:600; font-size:13px; }
    .danger-title { font-size:13px; font-weight:500; margin:0 0 6px; }
    .danger-item { font-size:12px; color:#A32D2D; background:#FCEBEB; padding:5px 10px; border-radius:6px; margin-bottom:4px; }
  `]
})
export class RouteComponent {
  fromLat = 0; fromLng = 0;
  toLat   = 0; toLng   = 0;
  route:   SafeRoute | null = null;
  loading  = false;

  scoreToColor = scoreToColor;

  constructor(private mapSvc: MapService) {}

  fillCurrentLocation(): void {
    navigator.geolocation.getCurrentPosition(pos => {
      this.fromLat = pos.coords.latitude;
      this.fromLng = pos.coords.longitude;
    });
  }

  planRoute(): void {
    this.loading = true;
    this.mapSvc.getSafeRoute(this.fromLat, this.fromLng, this.toLat, this.toLng).subscribe({
      next: (r) => { this.route = r; this.loading = false; },
      error: ()  => { this.loading = false; }
    });
  }
}
