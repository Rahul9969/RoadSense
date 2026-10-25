import React, { useState } from 'react';
import { Navigation, Clock, CheckCircle2, AlertTriangle, Eye } from 'lucide-react';
import type { IssueReport } from '../type';
import {
  getStatusColor,
  getStatusLabel,
  getStatusBadgeClasses,
  formatDate,
  formatConfidence,
  getImageSource,
  getSeverityColor,
} from '../functions';

interface IssueCardProps {
  issue: IssueReport;
  onUpdateStatus: (id: number, newStatus: string) => Promise<void>;
  onOpenImage: (imageUrl: string) => void;
  isSelected?: boolean;
}

export const IssueCard: React.FC<IssueCardProps> = ({
  issue,
  onUpdateStatus,
  onOpenImage,
  isSelected,
}) => {
  const [isUpdating, setIsUpdating] = useState(false);
  const imageSrc = getImageSource(issue);
  const statusClasses = getStatusBadgeClasses(issue.status);

  const handleAction = async (newStatus: string) => {
    try {
      setIsUpdating(true);
      await onUpdateStatus(issue.id, newStatus);
    } finally {
      setIsUpdating(false);
    }
  };

  return (
    <div
      className={`bg-white rounded-3xl p-5 sm:p-6 shadow-md border transition-all ${
        isSelected ? 'border-purple-500 ring-2 ring-purple-200' : 'border-gray-100 hover:border-gray-200'
      }`}
    >
      {/* Top Header Row */}
      <div className="flex items-start gap-4">
        {/* 1. Thumbnail Image (70x70) matching Flutter */}
        <div
          onClick={() => onOpenImage(imageSrc)}
          className="relative w-[70px] h-[70px] flex-shrink-0 rounded-2xl overflow-hidden bg-gray-100 border border-gray-200 cursor-pointer group shadow-sm"
        >
          <img
            src={imageSrc}
            alt={issue.label}
            className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-200"
          />
          <div className="absolute inset-0 bg-black/30 opacity-0 group-hover:opacity-100 flex items-center justify-center transition-opacity">
            <Eye className="w-5 h-5 text-white" />
          </div>
        </div>

        {/* 2. Hazard Label & Reporter */}
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 flex-wrap">
            <h3 className="text-base sm:text-lg font-bold text-[#1F2937] tracking-tight truncate">
              {issue.label.toUpperCase()}
            </h3>
            {issue.severity === 'critical' && (
              <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-bold bg-red-100 text-red-600 border border-red-200">
                <AlertTriangle className="w-3 h-3" />
                CRITICAL
              </span>
            )}
          </div>
          <p className="text-xs text-[#6B7280] mt-0.5">
            By: <span className="font-semibold text-gray-700">{issue.reporter}</span>
          </p>
          <p className="text-[11px] text-gray-400 mt-0.5">
            Lat: {issue.location?.lat?.toFixed(4)}, Lng: {issue.location?.lng?.toFixed(4)}
          </p>
        </div>

        {/* 3. Status Badge Pill */}
        <div
          className={`px-3 py-1 rounded-full text-xs font-bold border ${statusClasses.bg} ${statusClasses.text} ${statusClasses.border}`}
        >
          {getStatusLabel(issue.status)}
        </div>
      </div>

      {/* AI Confidence Score */}
      <div className="mt-3 flex items-center gap-2 text-xs font-semibold text-blue-900/70">
        <span className="px-2 py-0.5 rounded-md bg-blue-50 border border-blue-100">
          AI Confidence: {formatConfidence(issue.confidence_score)}
        </span>
        <span className="text-gray-400">•</span>
        <span className="text-gray-500 font-normal">
          Severity: <strong style={{ color: getSeverityColor(issue.severity) }}>{issue.severity}</strong>
        </span>
      </div>

      {/* Description Text */}
      <p className="mt-2 text-sm text-[#4B5563] leading-relaxed">
        {issue.description || 'No description provided.'}
      </p>

      {/* Timestamp Row */}
      <div className="mt-3 flex items-center gap-1.5 text-xs text-[#6B7280]">
        <Clock className="w-3.5 h-3.5 text-gray-400" />
        <span>{formatDate(issue.timestamp)}</span>
      </div>

      {/* Action Buttons Matching Flutter Gradients */}
      <div className="mt-4 pt-3.5 border-t border-gray-100 flex items-center gap-2.5 flex-wrap">
        {issue.status !== 'deployed' && (
          <button
            onClick={() => handleAction('deployed')}
            disabled={isUpdating}
            className="inline-flex items-center gap-2 px-4 py-2 rounded-2xl bg-gradient-to-r from-[#F97316] to-[#F59E0B] text-white text-xs sm:text-sm font-bold shadow-sm hover:shadow-md hover:brightness-105 active:scale-95 transition-all disabled:opacity-50"
          >
            <Navigation className="w-4 h-4" />
            <span>Deploy</span>
          </button>
        )}

        {issue.status !== 'underprocessed' && issue.status !== 'resolved' && (
          <button
            onClick={() => handleAction('underprocessed')}
            disabled={isUpdating}
            className="inline-flex items-center gap-2 px-4 py-2 rounded-2xl bg-gradient-to-r from-[#3B82F6] to-[#6366F1] text-white text-xs sm:text-sm font-bold shadow-sm hover:shadow-md hover:brightness-105 active:scale-95 transition-all disabled:opacity-50"
          >
            <Clock className="w-4 h-4" />
            <span>Process</span>
          </button>
        )}

        {issue.status !== 'resolved' && (
          <button
            onClick={() => handleAction('resolved')}
            disabled={isUpdating}
            className="inline-flex items-center gap-2 px-4 py-2 rounded-2xl bg-gradient-to-r from-[#10B981] to-[#059669] text-white text-xs sm:text-sm font-bold shadow-sm hover:shadow-md hover:brightness-105 active:scale-95 transition-all disabled:opacity-50"
          >
            <CheckCircle2 className="w-4 h-4" />
            <span>Resolve</span>
          </button>
        )}
      </div>
    </div>
  );
};
