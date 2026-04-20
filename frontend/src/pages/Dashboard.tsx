import React, { useEffect, useState } from 'react';
import { Layout } from '../components/Layout';
import { Card } from '../components/Card';
import { CostCard } from '../components/CostCard';
import { Loading } from '../components/Loading';
import { Alert } from '../components/Alert';
import { ChatBox } from '../components/ChatBox';
import api from '../services/api';
import { DashboardData } from '../types';
import { Activity, AlertCircle, Zap, MessageCircle } from 'lucide-react';

export const Dashboard: React.FC = () => {
  const [dashboard, setDashboard] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [chatOpen, setChatOpen] = useState(false);

  useEffect(() => {
    fetchDashboard();
  }, []);

  const fetchDashboard = async () => {
    try {
      setLoading(true);
      const data = await api.getDashboard();
      setDashboard(data);
    } catch (err: any) {
      setError('Failed to load dashboard');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <Layout><Loading /></Layout>;

  return (
    <Layout>
      <div className="space-y-8">
        {error && <Alert type="error" message={error} onClose={() => setError('')} />}

        {/* Header */}
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
          <p className="text-gray-600 mt-1">Monitor your cloud costs across all providers</p>
        </div>

        {/* Cost Overview */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <CostCard
            title="Total Cost"
            amount={dashboard?.total_cost || 0}
            trend="up"
            trendPercent={5}
          />
          <CostCard
            title="Clouds Connected"
            amount={dashboard?.clouds_connected || 0}
            currency=""
          />
          <CostCard
            title="Active Recommendations"
            amount={dashboard?.active_recommendations || 0}
            currency=""
          />
          <CostCard
            title="Recent Alerts"
            amount={dashboard?.recent_alerts?.length || 0}
            currency=""
          />
        </div>

        {/* Cloud Providers */}
        {dashboard && dashboard.clouds.length > 0 && (
          <Card>
            <h2 className="text-2xl font-bold mb-6 flex items-center space-x-2">
              <Zap size={24} className="text-primary" />
              <span>Connected Cloud Providers</span>
            </h2>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {dashboard.clouds.map((cloud, idx) => (
                <div key={idx} className="bg-gray-50 p-4 rounded-lg border border-gray-200">
                  <h3 className="font-semibold text-gray-900 mb-2">{cloud.provider}</h3>
                  <p className="text-2xl font-bold text-primary mb-2">
                    ${cloud.total_cost.toFixed(2)}
                  </p>
                  <div className={`inline-block px-2 py-1 rounded text-sm font-semibold ${
                    cloud.is_fresh ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'
                  }`}>
                    {cloud.is_fresh ? 'Fresh' : 'Stale'}
                  </div>

                  {cloud.top_services.length > 0 && (
                    <div className="mt-4">
                      <p className="text-sm font-semibold text-gray-700 mb-2">Top Services:</p>
                      <ul className="space-y-1">
                        {cloud.top_services.slice(0, 3).map(([service, cost], sidx) => (
                          <li key={sidx} className="text-sm text-gray-600">
                            <span className="font-medium">{service}:</span> ${cost.toFixed(2)}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </Card>
        )}

        {/* Recent Alerts */}
        {dashboard && dashboard.recent_alerts.length > 0 && (
          <Card>
            <h2 className="text-2xl font-bold mb-6 flex items-center space-x-2">
              <AlertCircle size={24} className="text-warning" />
              <span>Recent Alerts</span>
            </h2>

            <div className="space-y-3">
              {dashboard.recent_alerts.map((alert, idx) => (
                <div key={idx} className="bg-gray-50 p-4 rounded-lg border border-gray-200 flex justify-between items-start">
                  <div>
                    <p className="font-semibold text-gray-900">{alert.title}</p>
                    <p className="text-sm text-gray-600">{alert.type}</p>
                  </div>
                  <span className={`px-2 py-1 rounded text-xs font-semibold ${
                    alert.status === 'TRIGGERED' ? 'bg-red-100 text-red-800' : 'bg-gray-100 text-gray-800'
                  }`}>
                    {alert.status}
                  </span>
                </div>
              ))}
            </div>
          </Card>
        )}

        {/* No Data */}
        {dashboard && dashboard.clouds_connected === 0 && (
          <Card>
            <div className="text-center py-12">
              <Activity size={48} className="mx-auto text-gray-300 mb-4" />
              <h3 className="text-xl font-semibold text-gray-900 mb-2">No clouds connected</h3>
              <p className="text-gray-600 mb-4">Connect your first cloud provider to get started</p>
            </div>
          </Card>
        )}
      </div>

      {/* Floating Chat Button */}
      <button
        onClick={() => setChatOpen(!chatOpen)}
        className="fixed bottom-6 right-6 bg-primary text-white p-4 rounded-full shadow-lg hover:bg-blue-600 transition z-30"
        title="Open CloudLens AI Chat"
      >
        <MessageCircle size={24} />
      </button>

      {/* Chat Box */}
      <ChatBox isOpen={chatOpen} onClose={() => setChatOpen(false)} />
    </Layout>
  );
};