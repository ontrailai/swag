import React from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { getConfig, updateConfig } from '../lib/api';
import { ConfigEditor } from '../components/ConfigEditor';
import { motion } from 'framer-motion';
import toast from 'react-hot-toast';

export const Settings: React.FC = () => {
  const queryClient = useQueryClient();

  const { data: config, isLoading } = useQuery({
    queryKey: ['config'],
    queryFn: getConfig,
  });

  const updateMutation = useMutation({
    mutationFn: updateConfig,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['config'] });
      toast.success('✅ Configuration saved successfully!');
    },
    onError: (error: any) => {
      toast.error(`❌ Failed to save: ${error.message}`);
    },
  });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center">
          <div className="animate-spin w-16 h-16 border-4 border-swag-neon-green border-t-transparent rounded-full mx-auto mb-4" />
          <p className="text-swag-neon-green">Loading configuration...</p>
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
        <h1 className="text-4xl font-black text-transparent bg-gradient-to-r from-swag-gold to-swag-neon-blue bg-clip-text mb-2">
          ⚙️ Configuration Settings
        </h1>
        <p className="text-swag-skull-white/70">
          Manage Azure, Google Sheets, and variance thresholds
        </p>
      </motion.div>

      {/* Config Editor */}
      {config && (
        <ConfigEditor
          config={config}
          onSave={async (updatedConfig) => {
            await updateMutation.mutateAsync(updatedConfig);
          }}
        />
      )}
    </div>
  );
};
