import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { getProcessedFiles } from '../lib/api';
import { motion } from 'framer-motion';
import { FileText, Calendar, HardDrive } from 'lucide-react';

export const History: React.FC = () => {
  const { data: files, isLoading } = useQuery({
    queryKey: ['processed-files'],
    queryFn: getProcessedFiles,
    refetchInterval: 30000, // Refresh every 30s
  });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center">
          <div className="animate-spin w-16 h-16 border-4 border-swag-neon-green border-t-transparent rounded-full mx-auto mb-4" />
          <p className="text-swag-neon-green">Loading history...</p>
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
          📦 Processing History
        </h1>
        <p className="text-swag-skull-white/70">
          Recently processed invoice files
        </p>
      </motion.div>

      {/* Files List */}
      <div className="space-y-4">
        {files && files.length > 0 ? (
          files.map((file, index) => (
            <motion.div
              key={file.filename}
              className="swag-card flex items-center gap-4"
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.1 }}
            >
              <FileText className="w-10 h-10 text-swag-neon-blue" />
              <div className="flex-1">
                <h3 className="font-bold text-lg text-swag-neon-green">{file.filename}</h3>
                <div className="flex gap-4 mt-1 text-sm text-swag-skull-white/70">
                  <div className="flex items-center gap-1">
                    <Calendar className="w-4 h-4" />
                    {file.modified ? new Date(file.modified).toLocaleString() : 'N/A'}
                  </div>
                  <div className="flex items-center gap-1">
                    <HardDrive className="w-4 h-4" />
                    {(file.size / 1024).toFixed(1)} KB
                  </div>
                </div>
              </div>
            </motion.div>
          ))
        ) : (
          <div className="swag-card text-center py-12">
            <FileText className="w-16 h-16 mx-auto mb-4 text-swag-skull-white/30" />
            <p className="text-swag-skull-white/50">No processed files yet</p>
            <p className="text-sm text-swag-skull-white/30 mt-2">
              Upload and process invoices to see them here
            </p>
          </div>
        )}
      </div>
    </div>
  );
};
