import L from 'leaflet';
import type { HazardStatus, HazardSeverity, IssueReport } from './type';

/**
 * Returns the hex color string corresponding to a hazard status.
 * Matches Flutter admin client exact hex palette.
 * @param status - The current status of the road hazard.
 * @returns The hex color string.
 */
export function getStatusColor(status: string): string {
  switch (status.toLowerCase()) {
    case 'reported':
      return '#EF4444'; // Red (Color(0xFFEF4444))
    case 'deployed':
      return '#F59E0B'; // Amber / Orange (Color(0xFFF59E0B))
    case 'underprocessed':
      return '#3B82F6'; // Blue (Color(0xFF3B82F6))
    case 'resolved':
      return '#10B981'; // Green (Color(0xFF10B981))
    default:
      return '#6B7280';
  }
}

/**
 * Returns human-readable label for a hazard status.
 * @param status - The raw hazard status string.
 * @returns Formatted human-readable label.
 */
export function getStatusLabel(status: string): string {
  switch (status.toLowerCase()) {
    case 'reported':
      return 'Reported';
    case 'deployed':
      return 'Deployed';
    case 'underprocessed':
      return 'Under Process';
    case 'resolved':
      return 'Resolved';
    default:
      return status;
  }
}

/**
 * Returns Tailwind CSS badge classes for a given status.
 * @param status - Hazard status.
 * @returns Class names for background and text colors.
 */
export function getStatusBadgeClasses(status: string): { bg: string; text: string; border: string } {
  switch (status.toLowerCase()) {
    case 'reported':
      return { bg: 'bg-red-500/15', text: 'text-red-500', border: 'border-red-500/30' };
    case 'deployed':
      return { bg: 'bg-amber-500/15', text: 'text-amber-500', border: 'border-amber-500/30' };
    case 'underprocessed':
      return { bg: 'bg-blue-500/15', text: 'text-blue-500', border: 'border-blue-500/30' };
    case 'resolved':
      return { bg: 'bg-emerald-500/15', text: 'text-emerald-500', border: 'border-emerald-500/30' };
    default:
      return { bg: 'bg-gray-500/15', text: 'text-gray-500', border: 'border-gray-500/30' };
  }
}

/**
 * Returns the hex color string for hazard severity.
 * @param severity - Severity level ('low', 'medium', 'critical').
 * @returns Hex color string.
 */
export function getSeverityColor(severity?: string): string {
  switch (severity?.toLowerCase()) {
    case 'critical':
      return '#DC2626';
    case 'medium':
      return '#EA580C';
    case 'low':
      return '#16A34A';
    default:
      return '#6B7280';
  }
}

/**
 * Formats ISO timestamp to user-friendly local date-time string.
 * @param isoString - ISO formatted timestamp.
 * @returns User-friendly date and time.
 */
export function formatDate(isoString?: string): string {
  if (!isoString) return 'Recent';
  try {
    let raw = isoString.trim();
    // If ISO timestamp has no timezone offset (no Z, no +/-offset), append Z so browser converts UTC to user local time
    if (raw.includes('T') && !raw.endsWith('Z') && !/[+-]\d{2}:?\d{2}$/.test(raw)) {
      raw = raw + 'Z';
    }
    const d = new Date(raw);
    if (isNaN(d.getTime())) return isoString;
    return d.toLocaleString(undefined, {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      hour12: true,
    });
  } catch {
    return 'Recent';
  }
}

/**
 * Formats AI confidence score as percentage string.
 * @param score - Float between 0.0 and 1.0.
 * @returns Formatted percentage (e.g. "94.2%").
 */
export function formatConfidence(score?: number): string {
  if (score === undefined || score === null) return '85.0%';
  const val = score > 1 ? score : score * 100;
  return `${val.toFixed(1)}%`;
}

/**
 * Resolves the displayable image source from an issue report.
 * Supports S3 HTTPS URLs, local URLs, and base64 payloads seamlessly.
 * @param issue - The hazard report.
 * @returns Image src string.
 */
export function getImageSource(issue: IssueReport): string {
  if (issue.image_url && issue.image_url.startsWith('http')) {
    return issue.image_url;
  }
  if (issue.segmented_image && issue.segmented_image.length > 50) {
    if (issue.segmented_image.startsWith('data:image')) {
      return issue.segmented_image;
    }
    return `data:image/jpeg;base64,${issue.segmented_image}`;
  }
  if (issue.image && issue.image.startsWith('http')) {
    return issue.image;
  }
  return 'https://images.unsplash.com/photo-1515162816999-a0c47dc192f7?w=300&auto=format&fit=crop';
}

/**
 * Creates a custom HTML Leaflet pin marker colored according to status.
 * Matches Flutter map location_on icon pin look.
 * @param status - The hazard status.
 * @returns Leaflet DivIcon instance.
 */
export function createCustomMarkerIcon(status: string): L.DivIcon {
  const color = getStatusColor(status);
  const html = `
    <div style="position: relative; width: 34px; height: 34px; display: flex; align-items: center; justify-content: center;">
      <div style="
        width: 32px;
        height: 32px;
        background: ${color};
        border-radius: 50% 50% 50% 0;
        transform: rotate(-45deg);
        box-shadow: 0 4px 10px rgba(0,0,0,0.35);
        display: flex;
        align-items: center;
        justify-content: center;
        border: 2px solid #ffffff;
      ">
        <div style="
          width: 10px;
          height: 10px;
          background: #ffffff;
          border-radius: 50%;
          transform: rotate(45deg);
        "></div>
      </div>
    </div>
  `;

  return L.divIcon({
    className: 'custom-roadsense-marker',
    html,
    iconSize: [34, 34],
    iconAnchor: [17, 34],
    popupAnchor: [0, -32],
  });
}
