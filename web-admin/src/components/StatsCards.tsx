import React from 'react';
import { AlertCircle, Navigation, Clock, CheckCircle2, Flame, Layers } from 'lucide-react';
import type { AdminStats } from '../type';

interface StatsCardsProps {
  stats: AdminStats;
  activeStatus: string;
  onSelectStatus: (status: string) => void;
}

export const StatsCards: React.FC<StatsCardsProps> = ({
  stats,
  activeStatus,
  onSelectStatus,
}) => {
  const cards = [
    {
      id: 'all',
      label: 'Total Hazards',
      count: stats.total,
      icon: Layers,
      color: 'text-purple-600',
      bgColor: 'bg-purple-50',
      borderColor: 'border-purple-200',
      activeRing: 'ring-2 ring-purple-500',
    },
    {
      id: 'reported',
      label: 'Reported',
      count: stats.reported,
      icon: AlertCircle,
      color: 'text-[#EF4444]',
      bgColor: 'bg-red-50',
      borderColor: 'border-red-200',
      activeRing: 'ring-2 ring-[#EF4444]',
    },
    {
      id: 'deployed',
      label: 'Crew Deployed',
      count: stats.deployed,
      icon: Navigation,
      color: 'text-[#F59E0B]',
      bgColor: 'bg-amber-50',
      borderColor: 'border-amber-200',
      activeRing: 'ring-2 ring-[#F59E0B]',
    },
    {
      id: 'underprocessed',
      label: 'Under Process',
      count: stats.underprocessed,
      icon: Clock,
      color: 'text-[#3B82F6]',
      bgColor: 'bg-blue-50',
      borderColor: 'border-blue-200',
      activeRing: 'ring-2 ring-[#3B82F6]',
    },
    {
      id: 'resolved',
      label: 'Resolved',
      count: stats.resolved,
      icon: CheckCircle2,
      color: 'text-[#10B981]',
      bgColor: 'bg-emerald-50',
      borderColor: 'border-emerald-200',
      activeRing: 'ring-2 ring-[#10B981]',
    },
    {
      id: 'critical',
      label: 'Critical (SNS)',
      count: stats.critical,
      icon: Flame,
      color: 'text-rose-600',
      bgColor: 'bg-rose-50',
      borderColor: 'border-rose-200',
      activeRing: 'ring-2 ring-rose-500',
    },
  ];

  return (
    <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3.5 mb-6">
      {cards.map((c) => {
        const Icon = c.icon;
        const isActive = activeStatus === c.id;

        return (
          <button
            key={c.id}
            onClick={() => onSelectStatus(c.id === 'all' ? 'all' : c.id)}
            className={`flex flex-col items-start p-3.5 rounded-2xl bg-white border ${
              isActive ? c.activeRing : c.borderColor
            } shadow-sm hover:shadow-md transition-all text-left relative overflow-hidden group`}
          >
            <div className="flex items-center justify-between w-full mb-2">
              <div className={`p-2 rounded-xl ${c.bgColor} ${c.color}`}>
                <Icon className="w-4 h-4" />
              </div>
              <span className="text-xl sm:text-2xl font-extrabold text-gray-900 tracking-tight">
                {c.count}
              </span>
            </div>
            <span className="text-xs font-semibold text-gray-600 group-hover:text-gray-900 transition-colors">
              {c.label}
            </span>
          </button>
        );
      })}
    </div>
  );
};
