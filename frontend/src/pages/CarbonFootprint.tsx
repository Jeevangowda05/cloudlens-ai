import React, { useMemo, useState } from 'react';
import { Layout } from '../components/Layout';
import { Card } from '../components/Card';
import { FreshnessIndicator } from '../components/FreshnessIndicator';
import { ProviderBadge } from '../components/ProviderBadge';
import { Leaf, Gauge, Cloud, TrendingDown } from 'lucide-react';

const carbonStats = [
  { title: 'Estimated CO₂ / Month', value: '1.84 tCO₂e', icon: Cloud },
  { title: 'Green Workloads', value: '68%', icon: Leaf },
  { title: 'Efficiency Gain (30d)', value: '14%', icon: TrendingDown },
];

const sustainabilityActions = [
  'Move low-latency tolerant workloads to lower-carbon regions.',
  'Enable autoscaling on underutilized compute pools.',
  'Shift batch jobs to off-peak hours for cleaner grid mix.',
];

export const CarbonFootprint: React.FC = () => {
  const [provider, setProvider] = useState('AWS');
  const [lastSyncedAt, setLastSyncedAt] = useState<Date | null>(new Date());
  const providerMultiplier = provider === 'AWS' ? 1 : provider === 'AZURE' ? 0.94 : 0.9;
  const sustainabilityScore = useMemo(() => Math.round(78 / providerMultiplier), [providerMultiplier]);
  const providerStats = useMemo(
    () =>
      carbonStats.map((item) => ({
        ...item,
        value:
          item.title === 'Estimated CO₂ / Month'
            ? `${(1.84 * providerMultiplier).toFixed(2)} tCO₂e`
            : item.title === 'Green Workloads'
              ? `${Math.round(68 + (provider === 'GCP' ? 5 : provider === 'AZURE' ? 2 : 0))}%`
              : `${Math.round(14 + (provider === 'GCP' ? 3 : provider === 'AZURE' ? 1 : 0))}%`,
      })),
    [provider, providerMultiplier]
  );

  return (
    <Layout>
      <div className="space-y-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 flex items-center space-x-2">
            <Leaf size={32} className="text-green-600" />
            <span>Carbon Footprint</span>
          </h1>
          <p className="text-gray-600 mt-1">
            Track cloud environmental impact with a sustainability score
          </p>
          <div className="mt-2 flex items-center gap-2">
            <ProviderBadge provider={provider} />
            <FreshnessIndicator timestamp={lastSyncedAt} />
          </div>
        </div>
        <Card>
          <label className="block text-sm font-semibold text-gray-700 mb-2">Cloud Provider</label>
          <select
            value={provider}
            onChange={(event) => {
              setProvider(event.target.value);
              setLastSyncedAt(new Date());
            }}
            className="w-full md:w-64 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
          >
            <option value="AWS">AWS</option>
            <option value="AZURE">Azure</option>
            <option value="GCP">GCP</option>
          </select>
        </Card>

        <Card>
          <div className="flex items-start justify-between gap-6">
            <div>
              <p className="text-gray-600 text-sm">Sustainability Score</p>
              <div className="flex items-center space-x-2 mt-2">
                <Gauge size={28} className="text-primary" />
                <p className="text-4xl font-bold text-gray-900">{sustainabilityScore}/100</p>
              </div>
            </div>
            <div className="w-full max-w-md">
              <div className="h-3 bg-gray-200 rounded-full overflow-hidden">
                <div
                  className="h-full bg-gradient-to-r from-green-400 to-green-600"
                  style={{ width: `${sustainabilityScore}%` }}
                />
              </div>
              <p className="text-sm text-gray-600 mt-2">
                Strong progress. Focus on region optimization to reach 85+.
              </p>
            </div>
          </div>
        </Card>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {providerStats.map((item) => (
            <Card key={item.title}>
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">{item.title}</p>
                  <p className="text-2xl font-bold text-gray-900 mt-2">{item.value}</p>
                </div>
                <item.icon size={28} className="text-primary" />
              </div>
            </Card>
          ))}
        </div>

        <Card>
          <h2 className="text-2xl font-bold mb-4">Top Sustainability Actions</h2>
          <ul className="space-y-3">
            {sustainabilityActions.map((action) => (
              <li key={action} className="p-4 bg-gray-50 rounded-lg text-gray-700">
                {action}
              </li>
            ))}
          </ul>
        </Card>
      </div>
    </Layout>
  );
};
