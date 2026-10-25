import type { IssueReport, AdminStats, UserAuth } from '../type';

const DEFAULT_API_BASE = '';

export function getApiBaseUrl(): string {
  if (typeof window !== 'undefined') {
    const custom = localStorage.getItem('roadsense_api_url');
    // If the browser stored localhost:6969 or 127.0.0.1 from a local run, ignore it when accessed from a remote host
    if (custom && custom !== 'http://127.0.0.1:6969' && custom !== 'http://localhost:6969') {
      return custom.trim().replace(/\/+$/, '');
    }
  }
  return (import.meta as any).env?.VITE_API_BASE_URL || DEFAULT_API_BASE;
}

export function setApiBaseUrl(url: string): void {
  const cleanUrl = url.trim().replace(/\/+$/, '');
  localStorage.setItem('roadsense_api_url', cleanUrl);
}

export function getStoredAuth(): UserAuth | null {
  try {
    const raw = localStorage.getItem('roadsense_auth');
    if (!raw) return null;
    return JSON.parse(raw);
  } catch {
    return null;
  }
}

export function setStoredAuth(auth: UserAuth | null): void {
  if (!auth) {
    localStorage.removeItem('roadsense_auth');
  } else {
    localStorage.setItem('roadsense_auth', JSON.stringify(auth));
  }
}

function getAuthHeaders(): HeadersInit {
  const auth = getStoredAuth();
  const headers: HeadersInit = {
    'Content-Type': 'application/json',
  };
  if (auth?.token) {
    headers['Authorization'] = `Bearer ${auth.token}`;
  }
  return headers;
}

export async function loginAdmin(email: string, password: string): Promise<UserAuth> {
  const base = getApiBaseUrl();
  const response = await fetch(`${base}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      email,
      password,
      role: true, // Administrator role required
    }),
  });

  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.error || 'Authentication failed. Please verify credentials.');
  }

  const userAuth: UserAuth = {
    token: data.token,
    username: data.username || 'Admin',
    email: data.email || email,
    is_admin: true,
  };

  setStoredAuth(userAuth);
  return userAuth;
}

export async function fetchAllReports(filters?: { status?: string; severity?: string; search?: string }): Promise<IssueReport[]> {
  const base = getApiBaseUrl();
  const params = new URLSearchParams();

  if (filters?.status && filters.status !== 'all') {
    params.set('status', filters.status);
  }
  if (filters?.severity && filters.severity !== 'all') {
    params.set('severity', filters.severity);
  }
  if (filters?.search && filters.search.trim()) {
    params.set('search', filters.search.trim());
  }

  const queryStr = params.toString() ? `?${params.toString()}` : '';
  const response = await fetch(`${base}/api/admin/reports${queryStr}`, {
    method: 'GET',
    headers: getAuthHeaders(),
  });

  if (!response.ok) {
    throw new Error(`Failed to fetch reports (Status: ${response.status})`);
  }

  const data = await response.json();
  return data.reports || [];
}

export async function updateReportStatus(reportId: number, newStatus: string): Promise<IssueReport> {
  const base = getApiBaseUrl();
  const response = await fetch(`${base}/api/admin/reports/${reportId}`, {
    method: 'PATCH',
    headers: getAuthHeaders(),
    body: JSON.stringify({ status: newStatus }),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.error || `Failed to update status to ${newStatus}`);
  }

  const data = await response.json();
  return data.report;
}

export async function fetchStats(): Promise<AdminStats> {
  const base = getApiBaseUrl();
  const response = await fetch(`${base}/api/admin/stats`, {
    method: 'GET',
    headers: getAuthHeaders(),
  });

  if (!response.ok) {
    throw new Error('Failed to fetch statistics');
  }

  return response.json();
}

export async function fetchCloudTelemetry(): Promise<import('../type').CloudTelemetry> {
  const base = getApiBaseUrl();
  const response = await fetch(`${base}/api/admin/cloud-telemetry`, {
    method: 'GET',
    headers: getAuthHeaders(),
  });

  if (!response.ok) {
    throw new Error('Failed to fetch cloud telemetry');
  }

  return response.json();
}

export async function fetchTriageAnalytics(): Promise<import('../type').TriageAnalytics> {
  const base = getApiBaseUrl();
  const response = await fetch(`${base}/api/admin/triage-analytics`, {
    method: 'GET',
    headers: getAuthHeaders(),
  });

  if (!response.ok) {
    throw new Error('Failed to fetch triage analytics');
  }

  return response.json();
}

