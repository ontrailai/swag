import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { getDashboardStats, getVarianceSummary } from '../lib/api';
import { motion } from 'framer-motion';
import { FileText, AlertTriangle, DollarSign, TrendingUp } from 'lucide-react';
import { VarianceTable } from '../components/VarianceTable';

export const Dashboard: React.FC = () => {
  const { data: stats, isLoading: statsLoading } = useQuery({
    queryKey: ['dashboard-stats'],
    queryFn: getDashboardStats,
    refetchInterval: 10000, // Refresh every 10s
  });

  const { data: variance, isLoading: varianceLoading } = useQuery({
    queryKey: ['variance-summary'],
    queryFn: getVarianceSummary,
    refetchInterval: 10000,
  });

  if (statsLoading || varianceLoading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center">
          <div className="animate-spin w-16 h-16 border-4 border-swag-neon-green border-t-transparent rounded-full mx-auto mb-4" />
          <p className="text-swag-neon-green">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <h1 className="text-4xl font-black text-transparent bg-gradient-to-r from-swag-neon-green to-swag-neon-blue bg-clip-text mb-2">
          📊 Performance Dashboard
        </h1>
        <p className="text-swag-skull-white/70">
          Real-time analytics and variance monitoring
        </p>
      </motion.div>

      {/* Stat Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <motion.div
          className="stat-card"
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.1 }}
        >
          <FileText className="w-12 h-12 mx-auto mb-3 text-swag-neon-blue" />
          <p className="stat-label">Files Processed</p>
          <p className="stat-value">{stats?.files_processed || 0}</p>
        </motion.div>

        <motion.div
          className="stat-card"
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.2 }}
        >
          <AlertTriangle className="w-12 h-12 mx-auto mb-3 text-yellow-400" />
          <p className="stat-label">Variance Alerts</p>
          <p className="stat-value">{stats?.variance_alerts || 0}</p>
        </motion.div>

        <motion.div
          className="stat-card"
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.3 }}
        >
          <DollarSign className="w-12 h-12 mx-auto mb-3 text-swag-gold" />
          <p className="stat-label">Impact Cost</p>
          <p className="stat-value">${stats?.impact_cost.toFixed(2) || '0.00'}</p>
        </motion.div>

        <motion.div
          className="stat-card"
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.4 }}
        >
          <TrendingUp className="w-12 h-12 mx-auto mb-3 text-swag-neon-green" />
          <p className="stat-label">Variance Breakdown</p>
          <div className="flex justify-center gap-4 mt-2">
            <span className="text-swag-neon-green text-xl font-bold">
              🟢 {stats?.variance_counts.green || 0}
            </span>
            <span className="text-yellow-400 text-xl font-bold">
              🟡 {stats?.variance_counts.yellow || 0}
            </span>
            <span className="text-red-500 text-xl font-bold">
              🔴 {stats?.variance_counts.red || 0}
            </span>
          </div>
        </motion.div>
      </div>

      {/* Recent Activity Table */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.5 }}
      >
        <h2 className="text-2xl font-bold text-swag-neon-green mb-4">
          📋 Recent Activity (Last 10 Items)
        </h2>
        <VarianceTable data={variance?.recent_data || []} />
      </motion.div>
    </div>
  );
};
