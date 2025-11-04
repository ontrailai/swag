import React, { useState } from 'react';
import { useMutation, useQuery } from '@tanstack/react-query';
import { uploadFiles, startProcessing, getProcessingStatus } from '../lib/api';
import { UploadZone } from '../components/UploadZone';
import { ProgressCard } from '../components/ProgressCard';
import { motion } from 'framer-motion';
import { Zap } from 'lucide-react';

export const Upload: React.FC = () => {
  const [selectedFiles, setSelectedFiles] = useState<FileList | null>(null);
  const [jobId, setJobId] = useState<string | null>(null);

  const uploadMutation = useMutation({
    mutationFn: uploadFiles,
  });

  const processMutation = useMutation({
    mutationFn: startProcessing,
    onSuccess: (data) => {
      setJobId(data.job_id);
    },
  });

  const { data: jobStatus } = useQuery({
    queryKey: ['job-status', jobId],
    queryFn: () => getProcessingStatus(jobId!),
    enabled: !!jobId,
    refetchInterval: (query) => {
      // Stop refetching when job is complete or failed
      const data = query.state.data;
      if (data?.status === 'completed' || data?.status === 'failed') {
        return false;
      }
      return 300; // Poll every 300ms for instant updates
    },
  });

  const handleFilesSelected = (files: FileList) => {
    setSelectedFiles(files);
  };

  const handleUploadAndProcess = async () => {
    if (!selectedFiles) return;

    // Upload files
    await uploadMutation.mutateAsync(selectedFiles);

    // Start processing
    await processMutation.mutateAsync();
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <h1 className="text-4xl font-black text-transparent bg-gradient-to-r from-swag-neon-green to-swag-neon-blue bg-clip-text mb-2">
          📄 Upload & Process
        </h1>
        <p className="text-swag-skull-white/70">
          Upload invoice PDFs for AI-powered pricing analysis
        </p>
      </motion.div>

      {/* Upload Zone */}
      <UploadZone
        onFilesSelected={handleFilesSelected}
        disabled={uploadMutation.isPending || processMutation.isPending}
      />

      {/* Process Button */}
      {selectedFiles && selectedFiles.length > 0 && (
        <motion.button
          className="swag-btn w-full flex items-center justify-center gap-2"
          onClick={handleUploadAndProcess}
          disabled={uploadMutation.isPending || processMutation.isPending}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
        >
          <Zap className="w-6 h-6" />
          {uploadMutation.isPending
            ? 'Uploading...'
            : processMutation.isPending
            ? 'Starting...'
            : '⚡ RUN ANALYSIS →'}
        </motion.button>
      )}

      {/* Progress Card */}
      {jobStatus && (
        <ProgressCard
          jobId={jobId}
          status={jobStatus.status}
          progress={jobStatus.progress}
          message={jobStatus.message}
        />
      )}

      {/* Results */}
      {jobStatus?.status === 'completed' && jobStatus.results && (
        <motion.div
          className="swag-card"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <h2 className="text-2xl font-bold text-swag-neon-green mb-4">
            ✅ Processing Complete!
          </h2>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
            <div className="text-center">
              <p className="text-sm text-swag-skull-white/70">Total Files</p>
              <p className="text-3xl font-bold text-swag-neon-blue">
                {jobStatus.results.total_files}
              </p>
            </div>
            <div className="text-center">
              <p className="text-sm text-swag-skull-white/70">Successful</p>
              <p className="text-3xl font-bold text-swag-neon-green">
                {jobStatus.results.successful_files.length}
              </p>
            </div>
            <div className="text-center">
              <p className="text-sm text-swag-skull-white/70">Rows Written</p>
              <p className="text-3xl font-bold text-swag-gold">
                {jobStatus.results.total_rows_written}
              </p>
            </div>
            <div className="text-center">
              <p className="text-sm text-swag-skull-white/70">Variance</p>
              <div className="flex justify-center gap-2 mt-1">
                <span className="text-lg">🟢 {jobStatus.results.variance_counts['🟢']}</span>
                <span className="text-lg">🟡 {jobStatus.results.variance_counts['🟡']}</span>
                <span className="text-lg">🔴 {jobStatus.results.variance_counts['🔴']}</span>
              </div>
            </div>
          </div>

          {jobStatus.results.sheet_url && (
            <a
              href={jobStatus.results.sheet_url}
              target="_blank"
              rel="noopener noreferrer"
              className="swag-btn-secondary block text-center"
            >
              📊 View Google Sheet →
            </a>
          )}
        </motion.div>
      )}
    </div>
  );
};
