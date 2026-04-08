// admin/admin.component.ts
import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { AdminService } from '../shared/services/admin.service';
import { AdminAnalytics } from '../shared/models/models';

@Component({
  selector: 'app-admin',
  standalone: true,
  imports: [CommonModule, RouterLink],
  templateUrl: './admin.component.html'
})
export class AdminComponent implements OnInit {
  analytics: AdminAnalytics | null = null;
  reports: any[]    = [];
  hotspots: any[]   = [];
  activeTab         = 'dashboard';
  loading           = true;

  constructor(private adminService: AdminService) {}

  ngOnInit(): void {
    this.loadAnalytics();
    this.loadReports();
    this.loadHotspots();
  }

  loadAnalytics(): void {
    this.adminService.getAnalytics().subscribe({
      next: (res) => { this.analytics = res; this.loading = false; }
    });
  }

  loadReports(): void {
    this.adminService.getAllReports({ resolved: 'false', limit: 50 }).subscribe({
      next: (res) => { this.reports = res.reports; }
    });
  }

  loadHotspots(): void {
    this.adminService.getHotspots().subscribe({
      next: (res) => { this.hotspots = res.hotspots; }
    });
  }

  resolveReport(id: number): void {
    this.adminService.resolveReport(id).subscribe({
      next: () => {
        this.reports = this.reports.filter(r => r.id !== id);
        if (this.analytics) this.analytics.summary.open_reports--;
      }
    });
  }

  getSeverityLabel(s: number): string {
    return ['', 'Low', 'Minor', 'Moderate', 'High', 'Critical'][s] || 'Unknown';
  }

  getSeverityColor(s: number): string {
    const colors = ['', '#888', '#EF9F27', '#D85A30', '#E24B4A', '#991F1F'];
    return colors[s] || '#888';
  }
}
