// shared/models/models.ts — All TypeScript interfaces for SafeWalk

export interface User {
  id: number;
  name: string;
  email: string;
  role: 'user' | 'authority' | 'admin';
  trust_score: number;
  is_verified: boolean;
  emergency_contacts?: EmergencyContact[];
}

export interface EmergencyContact {
  name: string;
  phone: string;
  email: string;
}

export interface Report {
  id: number;
  user_id: number;
  lat: number;
  lng: number;
  street_name: string;
  street_id: string;
  incident_type: IncidentType;
  severity: number;
  description?: string;
  photo_url?: string;
  anonymous: boolean;
  resolved: boolean;
  reported_at: string;
  reporter_name?: string;
}

export type IncidentType =
  | 'poor_lighting'
  | 'suspicious_person'
  | 'harassment'
  | 'assault'
  | 'eve_teasing'
  | 'theft_robbery'
  | 'drunk_crowd'
  | 'broken_cctv'
  | 'isolated_road'
  | 'general_unsafe';

export interface StreetScore {
  id: number;
  street_id: string;
  street_name: string;
  lat: number;
  lng: number;
  score: number;
  score_day: number;
  score_night: number;
  active_report_count: number;
  trend: 'improving' | 'stable' | 'worsening';
  escalated: boolean;
  last_updated: string;
}

export interface SafeRoute {
  route_id: number;
  waypoints: RouteWaypoint[];
  avg_score: number;
  direct_dist_m: number;
  danger_streets: StreetScore[];
  safety_verdict: 'safe' | 'moderate' | 'dangerous';
}

export interface RouteWaypoint {
  lat: number;
  lng: number;
  score?: number;
  street_name?: string;
  label?: string;
}

export interface SosAlert {
  id: number;
  lat: number;
  lng: number;
  address?: string;
  resolved: boolean;
  triggered_at: string;
}

export interface Notification {
  id: number;
  type: string;
  message: string;
  is_read: boolean;
  created_at: string;
}

export interface AdminAnalytics {
  summary: {
    total_reports: number;
    open_reports: number;
    total_users: number;
    danger_streets: number;
    sos_today: number;
  };
  incident_breakdown: { incident_type: string; count: number }[];
  worst_streets: StreetScore[];
}
