import React, { useState, useEffect, useMemo, useCallback } from 'react';
import { Toaster, toast } from 'sonner';
import { Search, Filter, AlertTriangle } from 'lucide-react';
import type { IssueReport, AdminStats, UserAuth } from './type';
import { getStoredAuth, setStoredAuth, fetchAllReports, updateReportStatus, fetchStats } from './services/api';
import { Header } from './components/Header';
import { StatsCards } from './components/StatsCards';
import { MapSection } from './components/MapSection';
import { IssueCard } from './components/IssueCard';
import { ImageModal } from './components/ImageModal';
import { SkeletonLoader } from './components/SkeletonLoader';
import { ApiConfigModal } from './components/ApiConfigModal';
import { LoginView } from './components/LoginView';

export function App() {
  const [user, setUser] = useState<UserAuth | null>(() => getStoredAuth());
  const [issues, setIssues] = useState<IssueReport[]>([]);
  const [stats, setStats] = useState<AdminStats>({
    total: 0,
    reported: 0,
    deployed: 0,
    underprocessed: 0,
    resolved: 0,
    critical: 0,
  });

  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [isRefreshing, setIsRefreshing] = useState<boolean>(false);
  const [activeStatus, setActiveStatus] = useState<string>('all');
  const [activeSeverity, setActiveSeverity] = useState<string>('all');
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [selectedIssueId, setSelectedIssueId] = useState<number | null>(null);
  const [previewImageUrl, setPreviewImageUrl] = useState<string | null>(null);
  const [isConfigOpen, setIsConfigOpen] = useState<boolean>(false);

  // Load issues and statistics from backend
  const loadData = useCallback(async () => {
    try {
      setIsRefreshing(true);
      const [fetchedIssues, fetchedStats] = await Promise.all([
        fetchAllReports(),
        fetchStats().catch(() => null),
      ]);

      setIssues(fetchedIssues);

      if (fetchedStats) {
        setStats(fetchedStats);
      } else {
        // Compute statistics fallback
        setStats({
          total: fetchedIssues.length,
          reported: fetchedIssues.filter((i) => i.status === 'reported').length,
          deployed: fetchedIssues.filter((i) => i.status === 'deployed').length,
          underprocessed: fetchedIssues.filter((i) => i.status === 'underprocessed').length,
          resolved: fetchedIssues.filter((i) => i.status === 'resolved').length,
          critical: fetchedIssues.filter((i) => i.severity === 'critical').length,
        });
      }
    } catch (err: any) {
      console.error('Error loading reports:', err);
      toast.error('Failed to connect to backend: ' + (err.message || 'Server offline'));
    } finally {
      setIsLoading(false);
      setIsRefreshing(false);
    }
  }, []);

  // Check auth and initial fetch
  useEffect(() => {
    if (user) {
      loadData();
    } else {
      setIsLoading(false);
    }
  }, [user, loadData]);

  // Update Status handler with optimistic update and toast feedback
  const handleUpdateStatus = async (id: number, newStatus: string) => {
    try {
      await updateReportStatus(id, newStatus);
      setIssues((prev) =>
        prev.map((item) => (item.id === id ? { ...item, status: newStatus as any } : item))
      );
      toast.success(`Status updated to ${newStatus.toUpperCase()}`);
      // Refresh stats
      fetchStats().then((s) => setStats(s)).catch(() => {});
    } catch (err: any) {
      toast.error(err.message || 'Could not update status');
      throw err;
    }
  };

  const handleLogout = () => {
    setStoredAuth(null);
    setUser(null);
    toast.info('Signed out of administration portal');
  };

  // Filtered issues list based on search, status pill, and severity
  const filteredIssues = useMemo(() => {
    return issues.filter((issue) => {
      // Status filter
      if (activeStatus !== 'all' && issue.status?.toLowerCase() !== activeStatus.toLowerCase()) {
        if (activeStatus === 'critical') {
          if (issue.severity?.toLowerCase() !== 'critical') return false;
        } else {
          return false;
        }
      }

      // Severity filter
      if (activeSeverity !== 'all' && issue.severity?.toLowerCase() !== activeSeverity.toLowerCase()) {
        return false;
      }

      // Search query filter
      if (searchQuery.trim()) {
        const query = searchQuery.toLowerCase();
        const matchesLabel = issue.label?.toLowerCase().includes(query);
        const matchesReporter = issue.reporter?.toLowerCase().includes(query);
        const matchesDesc = issue.description?.toLowerCase().includes(query);
        return matchesLabel || matchesReporter || matchesDesc;
      }

      return true;
    });
  }, [issues, activeStatus, activeSeverity, searchQuery]);

  if (!user) {
    return (
      <>
        <Toaster position="top-right" richColors />
        <LoginView onLoginSuccess={(auth) => setUser(auth)} />
      </>
    );
  }

  return (
    <div className="min-h-screen bg-[#F8F9FA] flex flex-col font-sans">
      <Toaster position="top-right" richColors />

      {/* Header matching Flutter gradient */}
      <Header
        user={user}
        onLogout={handleLogout}
        onRefresh={loadData}
        onOpenSettings={() => setIsConfigOpen(true)}
        isRefreshing={isRefreshing}
      />

      {/* Main Content Area */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {/* KPI Counter Cards */}
        <StatsCards
          stats={stats}
          activeStatus={activeStatus}
          onSelectStatus={(s) => setActiveStatus(s)}
        />

        {/* Map Section */}
        <MapSection
          issues={filteredIssues}
          selectedIssueId={selectedIssueId}
          onSelectIssue={(issue) => {
            setSelectedIssueId(issue.id);
            const el = document.getElementById(`issue-card-${issue.id}`);
            el?.scrollIntoView({ behavior: 'smooth', block: 'center' });
          }}
        />

        {/* Search, Filter & Actions Toolbar */}
        <div className="bg-white rounded-2xl p-4 shadow-sm border border-gray-100 mb-6 flex flex-col sm:flex-row items-center justify-between gap-3.5">
          {/* Search Bar */}
          <div className="relative w-full sm:w-80">
            <Search className="w-4 h-4 text-gray-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search by label, user, or details..."
              className="w-full pl-9 pr-3.5 py-2 rounded-xl border border-gray-200 text-xs sm:text-sm focus:outline-none focus:ring-2 focus:ring-purple-500"
            />
          </div>

          {/* Status and Severity Filters */}
          <div className="flex items-center gap-2.5 w-full sm:w-auto overflow-x-auto pb-1 sm:pb-0">
            <div className="flex items-center gap-1.5 bg-gray-50 p-1 rounded-xl border border-gray-200 text-xs">
              <span className="px-2 text-gray-500 font-semibold flex items-center gap-1">
                <Filter className="w-3 h-3" />
                Status:
              </span>
              {(['all', 'reported', 'deployed', 'underprocessed', 'resolved'] as const).map((st) => (
                <button
                  key={st}
                  onClick={() => setActiveStatus(st)}
                  className={`px-2.5 py-1 rounded-lg font-bold capitalize transition-all ${
                    activeStatus === st
                      ? 'bg-purple-600 text-white shadow-sm'
                      : 'text-gray-600 hover:text-gray-900'
                  }`}
                >
                  {st === 'all' ? 'All' : st === 'underprocessed' ? 'In Process' : st}
                </button>
              ))}
            </div>

            {/* Severity selector */}
            <select
              value={activeSeverity}
              onChange={(e) => setActiveSeverity(e.target.value)}
              className="py-1.5 px-3 rounded-xl border border-gray-200 bg-white text-xs font-semibold text-gray-700 focus:outline-none focus:ring-2 focus:ring-purple-500"
            >
              <option value="all">All Severities</option>
              <option value="low">Low Severity</option>
              <option value="medium">Medium Severity</option>
              <option value="critical">Critical (SNS)</option>
            </select>
          </div>
        </div>

        {/* Active Issues Section Header */}
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl sm:text-2xl font-extrabold text-[#1F2937] tracking-tight">
            Active Issues ({filteredIssues.length})
          </h2>
          {activeStatus !== 'all' && (
            <button
              onClick={() => {
                setActiveStatus('all');
                setActiveSeverity('all');
                setSearchQuery('');
              }}
              className="text-xs text-purple-600 hover:text-purple-700 font-bold"
            >
              Clear filters
            </button>
          )}
        </div>

        {/* Issues List or Skeleton */}
        {isLoading ? (
          <SkeletonLoader />
        ) : filteredIssues.length === 0 ? (
          <div className="bg-white rounded-3xl p-12 text-center shadow-md border border-gray-100">
            <div className="w-14 h-14 rounded-2xl bg-purple-50 text-purple-600 flex items-center justify-center mx-auto mb-3">
              <AlertTriangle className="w-7 h-7" />
            </div>
            <h3 className="text-base font-bold text-gray-900">No Road Hazards Found</h3>
            <p className="text-xs text-gray-500 mt-1 max-w-sm mx-auto">
              There are no hazard reports matching your current filter criteria.
            </p>
          </div>
        ) : (
          <div className="space-y-4">
            {filteredIssues.map((issue) => (
              <div key={issue.id} id={`issue-card-${issue.id}`}>
                <IssueCard
                  issue={issue}
                  isSelected={selectedIssueId === issue.id}
                  onUpdateStatus={handleUpdateStatus}
                  onOpenImage={(url) => setPreviewImageUrl(url)}
                />
              </div>
            ))}
          </div>
        )}
      </main>

      {/* Full Image Modal matching Flutter _showFullImage */}
      <ImageModal
        imageUrl={previewImageUrl}
        onClose={() => setPreviewImageUrl(null)}
      />

      {/* Backend / Cloud Settings Modal */}
      <ApiConfigModal
        isOpen={isConfigOpen}
        onClose={() => setIsConfigOpen(false)}
        onSaved={loadData}
      />
    </div>
  );
}

export default App;
