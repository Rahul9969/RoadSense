import React from 'react';
import { LogOut, Cloud, RefreshCw, Settings, ShieldCheck } from 'lucide-react';
import type { UserAuth } from '../type';

interface HeaderProps {
  user: UserAuth | null;
  onLogout: () => void;
  onRefresh: () => void;
  onOpenSettings: () => void;
  isRefreshing: boolean;
}

export const Header: React.FC<HeaderProps> = ({
  user,
  onLogout,
  onRefresh,
  onOpenSettings,
  isRefreshing,
}) => {
  return (
    <header className="relative bg-gradient-to-r from-[#9333EA] via-[#7C3AED] to-[#2563EB] text-white shadow-md">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-8 pb-7">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
          {/* Title and Branding */}
          <div className="space-y-1">
            <div className="flex items-center gap-3">
              <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight text-white flex items-center gap-2">
                RoadSense Admin
              </h1>
              <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-white/20 text-white backdrop-blur-sm border border-white/25">
                <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse-dot" />
                AWS Cloud v2.0
              </span>
            </div>
            <p className="text-purple-100 text-sm font-medium flex items-center gap-2">
              <span>Municipality Issue Management</span>
              <span className="text-purple-300">•</span>
              <span className="text-purple-200">Logged in as {user?.username || 'Administrator'}</span>
            </p>
          </div>

          {/* Action Tools */}
          <div className="flex items-center gap-2.5 self-start md:self-auto">
            {/* Live Cloud Architecture Indicator */}
            <div className="hidden lg:flex items-center gap-2 px-3 py-1.5 rounded-xl bg-black/15 border border-white/10 text-xs text-purple-100 backdrop-blur-md shadow-sm">
              <Cloud className="w-4 h-4 text-sky-300" />
              <span>EC2 • RDS • S3 • SQS • SNS</span>
            </div>

            {/* Refresh Data Button */}
            <button
              onClick={onRefresh}
              disabled={isRefreshing}
              title="Refresh Reports"
              className="p-2.5 rounded-xl bg-white/10 hover:bg-white/20 active:scale-95 text-white transition-all backdrop-blur-sm border border-white/15 disabled:opacity-50"
            >
              <RefreshCw className={`w-4 h-4 ${isRefreshing ? 'animate-spin' : ''}`} />
            </button>

            {/* Backend Settings Button */}
            <button
              onClick={onOpenSettings}
              title="API & Cloud Settings"
              className="p-2.5 rounded-xl bg-white/10 hover:bg-white/20 active:scale-95 text-white transition-all backdrop-blur-sm border border-white/15"
            >
              <Settings className="w-4 h-4" />
            </button>

            {/* Logout Button */}
            <button
              onClick={onLogout}
              className="flex items-center gap-2 px-3.5 py-2 rounded-xl bg-white/15 hover:bg-red-500/80 active:scale-95 text-white text-sm font-semibold transition-all backdrop-blur-sm border border-white/20 shadow-sm"
            >
              <LogOut className="w-4 h-4" />
              <span className="hidden sm:inline">Logout</span>
            </button>
          </div>
        </div>
      </div>
    </header>
  );
};
