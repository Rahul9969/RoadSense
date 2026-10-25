import React from 'react';

export const SkeletonLoader: React.FC = () => {
  return (
    <div className="space-y-4">
      {/* Map Skeleton */}
      <div className="w-full h-[360px] sm:h-[400px] bg-white rounded-3xl p-4 shadow-md border border-gray-100 animate-pulse flex flex-col justify-between">
        <div className="h-6 bg-gray-200 rounded-md w-1/4 mb-4" />
        <div className="w-full h-full bg-gray-100 rounded-2xl flex items-center justify-center text-gray-300">
          Loading OpenStreetMap & Active Hazards...
        </div>
      </div>

      {/* Cards Skeletons */}
      {[1, 2, 3].map((i) => (
        <div
          key={i}
          className="bg-white rounded-3xl p-6 shadow-md border border-gray-100 animate-pulse space-y-4"
        >
          <div className="flex items-start gap-4">
            <div className="w-[70px] h-[70px] bg-gray-200 rounded-2xl flex-shrink-0" />
            <div className="flex-1 space-y-2">
              <div className="h-5 bg-gray-200 rounded w-1/3" />
              <div className="h-3.5 bg-gray-100 rounded w-1/4" />
              <div className="h-3 bg-gray-100 rounded w-1/2" />
            </div>
            <div className="w-20 h-6 bg-gray-200 rounded-full" />
          </div>
          <div className="h-10 bg-gray-100 rounded-xl w-full" />
          <div className="flex gap-2">
            <div className="w-24 h-9 bg-gray-200 rounded-2xl" />
            <div className="w-24 h-9 bg-gray-200 rounded-2xl" />
          </div>
        </div>
      ))}
    </div>
  );
};
