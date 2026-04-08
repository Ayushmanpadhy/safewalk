// report/report.component.ts
import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router, ActivatedRoute, RouterLink } from '@angular/router';
import { ReportService } from '../shared/services/report.service';

@Component({
  selector: 'app-report',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink],
  templateUrl: './report.component.html'
})
export class ReportComponent implements OnInit {
  form = {
    lat: '', lng: '', street_name: '',
    incident_type: '', description: '', anonymous: false
  };
  selectedFile: File | null = null;
  loading = false;
  success = false;
  error   = '';

  incidentTypes = [
    { value: 'poor_lighting',     label: 'Poor / No Lighting' },
    { value: 'suspicious_person', label: 'Suspicious Person' },
    { value: 'harassment',        label: 'Harassment' },
    { value: 'assault',           label: 'Assault' },
    { value: 'eve_teasing',       label: 'Eve-Teasing' },
    { value: 'theft_robbery',     label: 'Theft / Robbery' },
    { value: 'drunk_crowd',       label: 'Drunk Crowd' },
    { value: 'broken_cctv',       label: 'Broken CCTV' },
    { value: 'isolated_road',     label: 'Isolated Road' },
    { value: 'general_unsafe',    label: 'General Unsafe Feeling' }
  ];

  constructor(
    private reportService: ReportService,
    private router: Router,
    private route: ActivatedRoute
  ) {}

  ngOnInit(): void {
    // Pre-fill if coming from map click
    this.route.queryParams.subscribe(params => {
      if (params['lat'])    this.form.lat = params['lat'];
      if (params['lng'])    this.form.lng = params['lng'];
      if (params['street']) this.form.street_name = params['street'];
    });

    // Auto-fill GPS if not pre-filled
    if (!this.form.lat && navigator.geolocation) {
      navigator.geolocation.getCurrentPosition((pos) => {
        this.form.lat = pos.coords.latitude.toString();
        this.form.lng = pos.coords.longitude.toString();
      });
    }
  }

  onFileSelect(event: any): void {
    this.selectedFile = event.target.files[0] || null;
  }

  onSubmit(): void {
    if (!this.form.incident_type || !this.form.street_name) {
      this.error = 'Please fill all required fields';
      return;
    }
    this.loading = true;
    this.error   = '';

    const fd = new FormData();
    Object.entries(this.form).forEach(([k, v]) => fd.append(k, v.toString()));
    if (this.selectedFile) fd.append('photo', this.selectedFile);

    this.reportService.submitReport(fd).subscribe({
      next: () => {
        this.loading = false;
        this.success = true;
        setTimeout(() => this.router.navigate(['/map']), 2000);
      },
      error: (err) => {
        this.loading = false;
        this.error   = err.error?.error || 'Failed to submit report';
      }
    });
  }
}
