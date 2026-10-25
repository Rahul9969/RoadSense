import React from 'react';
import { Activity, Clock, ShieldAlert, Wrench, IndianRupee, Truck } from 'lucide-react';
import type { TriageAnalytics } from '../type';

interface TriageAnalyticsCardProps {
  analytics: TriageAnalytics | null;
  isLoading: boolean;
}

export const TriageAnalyticsCard: React.FC<TriageAnalyticsCardProps> = ({ analytics, isLoading }) => {
  if (isLoading || !analytics) {
    return (
      <div className="bg-white rounded-3xl p-6 shadow-md border border-gray-100 mb-6 animate-pulse">
        <div className="h-6 w-56 bg-gray-200 rounded mb-4" />
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="h-28 bg-gray-100 rounded-2xl" />
          ))}
        </div>
      </div>
    );
  }

  const pciColor = analytics.pci_score > 70 ? 'text-emerald-500' : (analytics.pci_score > 50 ? 'text-amber-500' : 'text-rose-500');
  const pciBg = analytics.pci_score > 70 ? 'bg-emerald-500' : (analytics.pci_score > 50 ? 'bg-amber-500' : 'bg-rose-500');

  return (
    <div className="bg-white rounded-3xl p-6 shadow-md border border-gray-100 mb-6">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between pb-4 border-b border-gray-100 mb-5 gap-2">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-xl bg-purple-500/10 flex items-center justify-center text-purple-600">
            <Activity className="w-4 h-4" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-gray-900 tracking-wide">
              Municipal AI Pavement Condition & Automated Triage
            </h3>
            <p className="text-xs text-gray-500">
              ASTM D6433 Pavement Condition Index (PCI) • Material Forecasting • SLA Enforcement
            </p>
          </div>
        </div>
        <span className="text-[11px] font-bold text-purple-700 bg-purple-50 px-3 py-1 rounded-full border border-purple-200">
          ASTM D6433 Compliant
        </span>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-5">
        {/* 1. PCI Score */}
        <div className="p-4 rounded-2xl bg-gray-50 border border-gray-100">
          <div className="flex items-center justify-between text-xs text-gray-500 mb-1">
            <span className="font-medium">Pavement Health Index</span>
            <span className={`font-bold ${pciColor}`}>{analytics.pci_rating}</span>
          </div>
          <div className="flex items-baseline gap-2">
            <span className={`text-2xl font-black ${pciColor}`}>{analytics.pci_score}</span>
            <span className="text-xs text-gray-400 font-semibold">/ 100 PCI</span>
          </div>
          <div className="w-full bg-gray-200 h-2 rounded-full mt-2.5 overflow-hidden">
            <div
              className={`h-full ${pciBg} transition-all duration-500`}
              style={{ width: `${analytics.pci_score}%` }}
            />
          </div>
        </div>

        {/* 2. Asphalt Tonnage Estimation */}
        <div className="p-4 rounded-2xl bg-gray-50 border border-gray-100">
          <div className="flex items-center justify-between text-xs text-gray-500 mb-1">
            <span className="font-medium">Estimated Asphalt Required</span>
            <Wrench className="w-4 h-4 text-orange-500" />
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-2xl font-black text-gray-900">{analytics.estimated_asphalt_tons}</span>
            <span className="text-xs text-gray-500 font-semibold">Tons (Cold-Mix)</span>
          </div>
          <p className="text-[11px] text-gray-400 mt-2">Calculated for road patches & repairs</p>
        </div>

        {/* 3. Budget Estimation */}
        <div className="p-4 rounded-2xl bg-gray-50 border border-gray-100">
          <div className="flex items-center justify-between text-xs text-gray-500 mb-1">
            <span className="font-medium">Municipal Budget Forecast</span>
            <IndianRupee className="w-4 h-4 text-emerald-600" />
          </div>
          <div className="flex items-baseline gap-1">
            <span className="text-xs font-bold text-gray-500">₹</span>
            <span className="text-2xl font-black text-gray-900">
              {analytics.estimated_budget_inr.toLocaleString('en-IN')}
            </span>
          </div>
          <p className="text-[11px] text-gray-400 mt-2">Material + labor mobilization cost</p>
        </div>

        {/* 4. Department Distribution */}
        <div className="p-4 rounded-2xl bg-gray-50 border border-gray-100">
          <div className="flex items-center justify-between text-xs text-gray-500 mb-1">
            <span className="font-medium">Department Triage</span>
            <Truck className="w-4 h-4 text-blue-500" />
          </div>
          <div className="space-y-1 text-xs text-gray-600 mt-1">
            {Object.entries(analytics.department_distribution).map(([dept, count]) => (
              <div key={dept} className="flex justify-between items-center text-[11px]">
                <span className="text-gray-500 truncate max-w-[130px]">{dept}</span>
                <span className="font-bold text-gray-800">{count}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Active SLA Countdowns */}
      {analytics.active_sla_countdowns.length > 0 && (
        <div className="bg-slate-50 rounded-2xl p-4 border border-slate-200/70">
          <div className="flex items-center gap-2 mb-3">
            <Clock className="w-3.5 h-3.5 text-rose-500" />
            <h4 className="text-xs font-bold text-gray-800 uppercase tracking-wider">
              Active Municipal SLA Countdown Timers
            </h4>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-2.5">
            {analytics.active_sla_countdowns.map((sla) => (
              <div
                key={sla.id}
                className="bg-white rounded-xl p-2.5 border border-gray-200 shadow-sm flex flex-col justify-between"
              >
                <div className="flex items-center justify-between mb-1">
                  <span className="text-[11px] font-bold text-gray-900 truncate">#{sla.id} {sla.label}</span>
                  <span className={`w-2 h-2 rounded-full ${sla.is_breached ? 'bg-rose-500 animate-ping' : 'bg-emerald-500'}`} />
                </div>
                <div className="flex items-baseline justify-between mt-1">
                  <span className="text-[10px] text-gray-400 capitalize">{sla.severity}</span>
                  <span className={`text-xs font-black ${sla.is_breached ? 'text-rose-600' : 'text-slate-700'}`}>
                    {sla.is_breached ? 'BREACHED' : `${sla.remaining_hours}h left`}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
