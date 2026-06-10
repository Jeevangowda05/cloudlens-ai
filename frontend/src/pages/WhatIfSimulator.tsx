import React, { useMemo, useState } from 'react';
import { Layout } from '../components/Layout';
import { Card } from '../components/Card';
import { Button } from '../components/Button';
import { FreshnessIndicator } from '../components/FreshnessIndicator';
import { ProviderBadge } from '../components/ProviderBadge';
import { FlaskConical, DollarSign, TrendingDown } from 'lucide-react';
import { getProviderMultiplier } from '../utils/multicloud';

export const WhatIfSimulator: React.FC = () => {
  const [monthlyCost, setMonthlyCost] = useState(4200);
  const [rightsizingPercent, setRightsizingPercent] = useState(10);
  const [reservedSavingsPercent, setReservedSavingsPercent] = useState(18);
  const [provider, setProvider] = useState('AWS');
  const [lastSyncedAt, setLastSyncedAt] = useState<Date | null>(new Date());

  const scenario = useMemo(() => {
    const baseline = monthlyCost * getProviderMultiplier(provider);
    const rightsizedCost = baseline * (1 - rightsizingPercent / 100);
    const finalCost = rightsizedCost * (1 - reservedSavingsPercent / 100);
    const monthlySavings = baseline - finalCost;
    return {
      projectedMonthly: finalCost,
      monthlySavings,
      yearlySavings: monthlySavings * 12,
      baseline,
    };
  }, [monthlyCost, provider, rightsizingPercent, reservedSavingsPercent]);

  return (
    <Layout>
      <div className="space-y-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 flex items-center space-x-2">
            <FlaskConical size={32} className="text-primary" />
            <span>What-If Simulator</span>
          </h1>
          <p className="text-gray-600 mt-1">Test cost changes before implementation</p>
          <div className="mt-2 flex items-center gap-2">
            <ProviderBadge provider={provider} />
            <FreshnessIndicator timestamp={lastSyncedAt} />
          </div>
        </div>

        <Card>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">Cloud Provider</label>
              <select
                value={provider}
                onChange={(e) => {
                  setProvider(e.target.value);
                  setLastSyncedAt(new Date());
                }}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
              >
                <option value="AWS">AWS</option>
                <option value="AZURE">Azure</option>
                <option value="GCP">GCP</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">Current Monthly Cost ($)</label>
              <input
                type="number"
                min={0}
                value={monthlyCost}
                onChange={(e) => setMonthlyCost(Number(e.target.value) || 0)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
              />
            </div>
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">Rightsizing Impact (%)</label>
              <input
                type="number"
                min={0}
                max={100}
                value={rightsizingPercent}
                onChange={(e) => setRightsizingPercent(Number(e.target.value) || 0)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
              />
            </div>
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">Reserved/Commitment Savings (%)</label>
              <input
                type="number"
                min={0}
                max={100}
                value={reservedSavingsPercent}
                onChange={(e) => setReservedSavingsPercent(Number(e.target.value) || 0)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
              />
            </div>
          </div>
        </Card>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <Card>
            <p className="text-xs text-gray-500">Provider-adjusted baseline</p>
            <p className="text-sm font-semibold text-gray-700 mt-1">${scenario.baseline.toFixed(2)}</p>
            <p className="text-sm text-gray-600">Projected Monthly Cost</p>
            <p className="text-3xl font-bold text-gray-900 mt-2">${scenario.projectedMonthly.toFixed(2)}</p>
          </Card>
          <Card>
            <p className="text-sm text-gray-600 flex items-center space-x-2">
              <TrendingDown size={16} />
              <span>Monthly Savings</span>
            </p>
            <p className="text-3xl font-bold text-success mt-2">${scenario.monthlySavings.toFixed(2)}</p>
          </Card>
          <Card>
            <p className="text-sm text-gray-600 flex items-center space-x-2">
              <DollarSign size={16} />
              <span>Yearly Savings</span>
            </p>
            <p className="text-3xl font-bold text-success mt-2">${scenario.yearlySavings.toFixed(2)}</p>
          </Card>
        </div>

        <Card>
          <h2 className="text-2xl font-bold mb-4">Suggested Experiments</h2>
          <div className="space-y-3">
            <div className="p-4 rounded-lg border border-gray-200">
              Increase rightsizing by 5% to compare extra savings on compute-heavy workloads.
            </div>
            <div className="p-4 rounded-lg border border-gray-200">
              Test commitments at 1-year vs 3-year terms before locking contracts.
            </div>
            <div className="p-4 rounded-lg border border-gray-200">
              Combine with region optimization for a blended savings scenario.
            </div>
          </div>
          <Button className="mt-4">Save Scenario</Button>
        </Card>
      </div>
    </Layout>
  );
};
