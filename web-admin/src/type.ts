/**
 * Shared Type Definitions for RoadSense Admin Portal
 */

export type HazardStatus = 'reported' | 'deployed' | 'underprocessed' | 'resolved';
export type HazardSeverity = 'low' | 'medium' | 'critical';

export interface LocationCoordinates {
  lat: number;
  lng: number;
}

export interface IssueReport {
  id: number;
  issue_id?: number;
  title: string;
  description: string;
  reporter: string;
  username?: string;
  location: LocationCoordinates;
  status: HazardStatus;
  severity: HazardSeverity;
  confidence_score: number;
  image_url?: string;
  segmented_image?: string;
  image?: string;
  timestamp: string;
  created_at?: string;
  label: string;
}

export interface AdminStats {
  total: number;
  reported: number;
  deployed: number;
  underprocessed: number;
  resolved: number;
  critical: number;
}

export interface UserAuth {
  token: string;
  username: string;
  email: string;
  is_admin: boolean;
}

export interface FilterState {
  status: string;
  severity: string;
  searchQuery: string;
}
