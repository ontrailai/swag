import React from 'react';
import { motion } from 'framer-motion';
import { Loader2, CheckCircle, XCircle } from 'lucide-react';

interface ProgressCardProps {
  jobId: string | null;
  status: 'pending' | 'processing' | 'completed' | 'failed' | null;
  progress: number;
  message: string;
}

export const ProgressCard: React.FC<ProgressCardProps> = ({
  status,
  progress,
  message,
}) => {
  if (!status) return null;

  return (
    <motion.div
      className="swag-card"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
    >
      <div className="flex items-center gap-4 mb-4">
        {status === 'processing' && (
          <Loader2 className="w-8 h-8 text-swag-neon-blue animate-spin" />
        )}
        {status === 'completed' && (
          <CheckCircle className="w-8 h-8 text-swag-neon-green" />
        )}
        {status === 'failed' && (
          <XCircle className="w-8 h-8 text-red-500" />
        )}
        <div className="flex-1">
          <h3 className="text-xl font-bold text-swag-neon-green">
            {status === 'processing' && '⚡ Processing Invoices...'}
            {status === 'completed' && '✅ Processing Complete!'}
            {status === 'failed' && '❌ Processing Failed'}
            {status === 'pending' && '⏳ Starting...'}
          </h3>
          <p className="text-sm text-swag-skull-white/70">{message}</p>
        </div>
      </div>

      <div className="swag-progress-bar">
        <motion.div
          className="swag-progress-fill"
          initial={{ width: 0 }}
          animate={{ width: `${progress * 100}%` }}
          transition={{ duration: 0.5 }}
        />
      </div>

      <p className="text-right text-sm text-swag-neon-green mt-2 font-bold">
        {Math.round(progress * 100)}%
      </p>
    </motion.div>
  );
};
