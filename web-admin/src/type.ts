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

export interface CloudTelemetry {
  timestamp: string;
  aws_region: string;
  sqs: {
    queue_name: string;
    queue_url: string;
    status: string;
    messages_available: number;
    messages_in_flight: number;
    dlq_status: string;
  };
  s3: {
    bucket_name: string;
    region: string;
    status: string;
    storage_class: string;
    encryption: string;
  };
  sns: {
    topic_arn: string;
    status: string;
    alert_routing: string;
  };
  lambda: {
    function_name: string;
    runtime: string;
    trigger: string;
    status: string;
    batch_size: number;
  };
  rds: {
    engine: string;
    host: string;
    status: string;
    pool_size: number;
  };
}

export interface TriageAnalytics {
  pci_score: number;
  pci_rating: 'Good' | 'Fair' | 'Critical';
  estimated_asphalt_tons: number;
  estimated_budget_inr: number;
  department_distribution: Record<string, number>;
  active_sla_countdowns: Array<{
    id: number;
    label: string;
    severity: string;
    remaining_hours: number;
    is_breached: boolean;
  }>;
}

