import React, { useEffect, useState } from 'react';
import { RefreshCw } from 'lucide-react';
import { formatRelativeTime } from '../utils/multicloud';

interface FreshnessIndicatorProps {
  timestamp?: string | Date | null;
  isSyncing?: boolean;
  isFresh?: boolean;
}

export const FreshnessIndicator: React.FC<FreshnessIndicatorProps> = ({ timestamp, isSyncing = false, isFresh = true }) => {
  const [, setTick] = useState(0);

  useEffect(() => {
    const timer = setInterval(() => setTick((value) => value + 1), 30000);
    return () => clearInterval(timer);
  }, []);

  return (
    <div className="inline-flex items-center gap-2 text-xs text-gray-600">
      <RefreshCw size={12} className={isSyncing ? 'animate-spin text-primary' : ''} />
      <span>{isSyncing ? 'Syncing live data...' : formatRelativeTime(timestamp)}</span>
      <span className={`px-2 py-0.5 rounded font-semibold ${isFresh ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'}`}>
        {isFresh ? 'Fresh' : 'Stale'}
      </span>
    </div>
  );
};
