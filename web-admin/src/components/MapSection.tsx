import React, { useMemo } from 'react';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import type { IssueReport } from '../type';
import { createCustomMarkerIcon, getStatusColor, getStatusLabel, getSeverityColor, getImageSource, formatDate } from '../functions';

interface MapSectionProps {
  issues: IssueReport[];
  selectedIssueId?: number | null;
  onSelectIssue: (issue: IssueReport) => void;
}

export const MapSection: React.FC<MapSectionProps> = ({
  issues,
  selectedIssueId,
  onSelectIssue,
}) => {
  // Default coordinate center (Kathmandu / Dhulikhel region from original project)
  const defaultCenter: [number, number] = useMemo(() => {
    if (issues.length > 0 && issues[0].location?.lat && issues[0].location?.lng) {
      return [issues[0].location.lat, issues[0].location.lng];
    }
    return [27.6194, 85.5388];
  }, [issues]);

  return (
    <div className="relative w-full h-[360px] sm:h-[400px] bg-white rounded-3xl shadow-md border border-gray-100 overflow-hidden mb-6">
      <MapContainer
        center={defaultCenter}
        zoom={13}
        scrollWheelZoom={false}
        className="w-full h-full"
      >
        <TileLayer
          attribution='&copy; Google Maps'
          url="https://mt{s}.google.com/vt/lyrs=m&x={x}&y={y}&z={z}"
          subdomains={['0', '1', '2', '3']}
        />

        {issues.map((issue) => {
          const lat = Number(issue.location?.lat) || 0;
          const lng = Number(issue.location?.lng) || 0;
          if (lat === 0 && lng === 0) return null;

          const isSelected = selectedIssueId === issue.id;
          const icon = createCustomMarkerIcon(issue.status);

          return (
            <Marker
              key={issue.id}
              position={[lat, lng]}
              icon={icon}
              eventHandlers={{
                click: () => onSelectIssue(issue),
              }}
            >
              <Popup className="roadsense-map-popup">
                <div className="p-3 w-56 text-left">
                  <div className="relative h-28 w-full rounded-lg overflow-hidden bg-gray-100 mb-2 border border-gray-200">
                    <img
                      src={getImageSource(issue)}
                      alt={issue.label}
                      className="w-full h-full object-cover"
                    />
                    <span
                      className="absolute top-1.5 right-1.5 px-2 py-0.5 rounded text-[10px] font-bold text-white shadow-sm"
                      style={{ backgroundColor: getStatusColor(issue.status) }}
                    >
                      {getStatusLabel(issue.status)}
                    </span>
                  </div>
                  <h4 className="font-bold text-sm text-gray-900 leading-tight mb-1">
                    {issue.label.toUpperCase()}
                  </h4>
                  <p className="text-xs text-gray-500 mb-2">By: {issue.reporter}</p>
                  <div className="flex items-center justify-between text-[11px] text-gray-600 border-t border-gray-100 pt-1.5">
                    <span>Severity: <strong style={{ color: getSeverityColor(issue.severity) }}>{issue.severity}</strong></span>
                    <span>{formatDate(issue.timestamp)}</span>
                  </div>
                </div>
              </Popup>
            </Marker>
          );
        })}
      </MapContainer>

      {/* Floating Legend Overlay matching Flutter */}
      <div className="absolute bottom-4 right-4 z-[400] bg-white/95 backdrop-blur-md rounded-2xl shadow-md border border-gray-100 p-3 pointer-events-auto">
        <span className="text-[11px] font-bold text-gray-800 uppercase tracking-wider block mb-2">
          Status Legend
        </span>
        <div className="space-y-1.5 text-xs text-gray-600">
          <div className="flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-[#EF4444]" />
            <span className="font-medium">Reported</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-[#F59E0B]" />
            <span className="font-medium">Deployed</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-[#3B82F6]" />
            <span className="font-medium">Under Process</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-[#10B981]" />
            <span className="font-medium">Resolved</span>
          </div>
        </div>
      </div>
    </div>
  );
};
