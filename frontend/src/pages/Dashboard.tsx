import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { getDashboardStats, getVarianceSummary } from '../lib/api';
import { motion } from 'framer-motion';
import { FileText, AlertTriangle, DollarSign, TrendingUp } from 'lucide-react';
import { VarianceTable } from '../components/VarianceTable';
import swagLogo from '../assets/swag-logo.svg';

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
        className="relative"
      >
        {/* Background watermark */}
        <div className="absolute -right-8 -top-8 opacity-5 pointer-events-none">
          <img src={swagLogo} alt="" className="w-48 h-48" />
        </div>

        <h1 className="text-3xl font-display font-black uppercase tracking-wider bg-gradient-to-r from-swag-neon-green to-swag-neon-blue bg-clip-text text-transparent mb-2 relative z-10">
          Performance Dashboard
        </h1>
        <p className="text-swag-skull-white/70 font-body relative z-10">
          Real-time analytics and variance monitoring
        </p>
      </motion.div>

      {/* Stat Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <motion.div
          className="stat-card relative overflow-hidden"
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.1 }}
          whileHover={{ scale: 1.05 }}
        >
          <div className="absolute inset-0 bg-gradient-to-br from-swag-neon-blue/10 to-transparent" />
          <FileText className="w-12 h-12 mx-auto mb-3 text-swag-neon-blue relative z-10" />
          <p className="stat-label relative z-10">Files Processed</p>
          <p className="stat-value relative z-10">{stats?.files_processed || 0}</p>
        </motion.div>

        <motion.div
          className="stat-card relative overflow-hidden"
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.2 }}
          whileHover={{ scale: 1.05 }}
        >
          <div className="absolute inset-0 bg-gradient-to-br from-yellow-400/10 to-transparent" />
          <AlertTriangle className="w-12 h-12 mx-auto mb-3 text-yellow-400 relative z-10" />
          <p className="stat-label relative z-10">Variance Alerts</p>
          <p className="stat-value relative z-10">{stats?.variance_alerts || 0}</p>
        </motion.div>

        <motion.div
          className="stat-card relative overflow-hidden"
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.3 }}
          whileHover={{ scale: 1.05 }}
        >
          <div className="absolute inset-0 bg-gradient-to-br from-swag-gold/10 to-transparent" />
          <DollarSign className="w-12 h-12 mx-auto mb-3 text-swag-gold relative z-10" />
          <p className="stat-label relative z-10">Impact Cost</p>
          <p className="stat-value relative z-10">${stats?.impact_cost.toFixed(2) || '0.00'}</p>
        </motion.div>

        <motion.div
          className="stat-card relative overflow-hidden"
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.4 }}
          whileHover={{ scale: 1.05 }}
        >
          <div className="absolute inset-0 bg-gradient-to-br from-swag-neon-green/10 to-transparent" />
          <TrendingUp className="w-12 h-12 mx-auto mb-3 text-swag-neon-green relative z-10" />
          <p className="stat-label relative z-10">Variance Breakdown</p>
          <div className="flex justify-center gap-4 mt-2 relative z-10">
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
        className="relative"
      >
        {/* Background watermark */}
        <div className="absolute -left-8 top-20 opacity-5 pointer-events-none">
          <img src={swagLogo} alt="" className="w-64 h-64" />
        </div>

        <h2 className="text-xl font-display font-bold uppercase tracking-wider text-swag-neon-green mb-4 relative z-10">
          Recent Activity
        </h2>
        <p className="text-sm text-swag-skull-white/50 mb-4 font-body relative z-10">
          Last 10 processed items
        </p>
        <VarianceTable data={variance?.recent_data || []} />
      </motion.div>
    </div>
  );
};
