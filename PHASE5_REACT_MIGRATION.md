# Phase 5: React + FastAPI Migration - Implementation Guide

## 🎯 Overview

Migrating SwagPricingTool from Streamlit prototype to production-grade React + FastAPI application with Swag Golf brand aesthetic.

**Status**: In Progress
**Started**: 2025-11-04
**Tech Stack**: React 18, TypeScript, Vite, Tailwind CSS, FastAPI, Python 3.x

---

## ✅ Completed Components

### 1. Backend (FastAPI)

**File**: `/backend/main.py`

**Endpoints Implemented**:
- `GET /` - API root
- `GET /health` - Health check
- `POST /upload` - Upload PDF files
- `POST /process` - Start processing job (background task)
- `GET /status/{job_id}` - Get processing status
- `GET /variance-summary` - Get variance summary with recent data
- `GET /dashboard-stats` - Get dashboard statistics
- `GET /config` - Get current configuration
- `POST /config/update` - Update configuration
- `GET /processed-files` - Get recently processed files

**Features**:
- CORS enabled for React frontend (localhost:5173, localhost:3000)
- Background job processing with job ID tracking
- File upload handling with validation
- Integration with existing Python pipeline (`main.py`)
- Configuration management (config.json)
- Google Sheets data fetching

### 2. Frontend Foundation

**Initialized**:
- React 18 + Vite + TypeScript
- Tailwind CSS with custom Swag Golf theme
- Dependencies: axios, @tanstack/react-query, framer-motion, lucide-react, react-router-dom

**Files Created**:
- `/frontend/tailwind.config.js` - Swag Golf brand colors and animations
- `/frontend/postcss.config.js` - PostCSS configuration
- `/frontend/src/index.css` - Complete Tailwind setup with Swag components
- `/frontend/src/lib/api.ts` - API client with TypeScript types

**Design System**:
- Dark theme (#0F0F0F base)
- Neon green accent (#32FF6A)
- Neon blue (#00BFFF)
- Gold accent (#D4AF37)
- Custom fonts: Orbitron (headers) + Inter (body)
- Predefined components: swag-card, swag-btn, upload-zone, stat-card, swag-input

---

## 📋 Remaining Implementation Tasks

### 3. Core React Components

#### 3.1 UploadZone Component

**File**: `/frontend/src/components/UploadZone.tsx`

```typescript
import React, { useState, useRef } from 'react';
import { Upload, FileText, X } from 'lucide-react';
import { motion } from 'framer-motion';

interface UploadZoneProps {
  onFilesSelected: (files: FileList) => void;
  disabled?: boolean;
}

export const UploadZone: React.FC<UploadZoneProps> = ({ onFilesSelected, disabled }) => {
  const [dragActive, setDragActive] = useState(false);
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const inputRef = useRef<HTMLInputElement>(null);

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    const files = e.dataTransfer.files;
    if (files && files.length > 0) {
      const pdfFiles = Array.from(files).filter(f => f.type === 'application/pdf');
      setSelectedFiles(pdfFiles);

      const fileList = new DataTransfer();
      pdfFiles.forEach(file => fileList.items.add(file));
      onFilesSelected(fileList.files);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    e.preventDefault();
    if (e.target.files && e.target.files.length > 0) {
      const files = Array.from(e.target.files);
      setSelectedFiles(files);
      onFilesSelected(e.target.files);
    }
  };

  const removeFile = (index: number) => {
    const newFiles = selectedFiles.filter((_, i) => i !== index);
    setSelectedFiles(newFiles);
  };

  return (
    <div className="space-y-4">
      <motion.div
        className={`upload-zone ${dragActive ? 'border-swag-neon-green shadow-neon-green' : ''}`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
        onClick={() => inputRef.current?.click()}
        whileHover={{ scale: 1.02 }}
        whileTap={{ scale: 0.98 }}
      >
        <Upload className="w-16 h-16 mx-auto mb-4 text-swag-neon-green" />
        <h3 className="text-2xl font-bold text-swag-neon-green mb-2">
          Drag & Drop PDFs Here
        </h3>
        <p className="text-swag-skull-white/70">
          or click to browse your files
        </p>
        <p className="text-sm text-swag-skull-white/50 mt-2">
          Supports: .pdf files only
        </p>
        <input
          ref={inputRef}
          type="file"
          multiple
          accept=".pdf"
          onChange={handleChange}
          className="hidden"
          disabled={disabled}
        />
      </motion.div>

      {selectedFiles.length > 0 && (
        <div className="swag-card">
          <h4 className="text-lg font-bold text-swag-neon-blue mb-3">
            ✅ {selectedFiles.length} File(s) Selected
          </h4>
          <div className="space-y-2">
            {selectedFiles.map((file, index) => (
              <motion.div
                key={index}
                className="flex items-center justify-between p-3 bg-swag-dark-tertiary rounded-lg"
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.1 }}
              >
                <div className="flex items-center gap-3">
                  <FileText className="w-5 h-5 text-swag-neon-green" />
                  <div>
                    <p className="text-sm font-medium">{file.name}</p>
                    <p className="text-xs text-swag-skull-white/50">
                      {(file.size / 1024).toFixed(1)} KB
                    </p>
                  </div>
                </div>
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    removeFile(index);
                  }}
                  className="text-red-500 hover:text-red-400 transition-colors"
                >
                  <X className="w-5 h-5" />
                </button>
              </motion.div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
```

#### 3.2 ProgressCard Component

**File**: `/frontend/src/components/ProgressCard.tsx`

```typescript
import React, { useEffect } from 'react';
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
```

#### 3.3 VarianceTable Component

**File**: `/frontend/src/components/VarianceTable.tsx`

```typescript
import React from 'react';
import { motion } from 'framer-motion';

interface VarianceTableProps {
  data: Array<Record<string, string>>;
}

export const VarianceTable: React.FC<VarianceTableProps> = ({ data }) => {
  if (!data || data.length === 0) {
    return (
      <div className="swag-card text-center py-12">
        <p className="text-swag-skull-white/50">No data available</p>
      </div>
    );
  }

  const columns = ['vendor_sku', 'description', 'unit_cost', 'variance_flag', 'variance_%', 'processed_date'];
  const displayColumns = columns.filter(col => data[0]?.[col] !== undefined);

  return (
    <div className="swag-card overflow-x-auto">
      <table className="w-full">
        <thead>
          <tr className="border-b-2 border-swag-neon-green/30">
            {displayColumns.map((col) => (
              <th
                key={col}
                className="px-4 py-3 text-left text-sm font-bold text-swag-neon-green uppercase tracking-wide"
              >
                {col.replace('_', ' ')}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {data.map((row, index) => (
            <motion.tr
              key={index}
              className="border-b border-swag-dark-tertiary hover:bg-swag-neon-green/5 transition-colors"
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.05 }}
            >
              {displayColumns.map((col) => (
                <td key={col} className="px-4 py-3 text-sm">
                  {col === 'variance_flag' ? (
                    <span className="text-xl">{row[col]}</span>
                  ) : (
                    <span className="text-swag-skull-white/90">{row[col]}</span>
                  )}
                </td>
              ))}
            </motion.tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};
```

#### 3.4 ConfigEditor Component

**File**: `/frontend/src/components/ConfigEditor.tsx`

```typescript
import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Save, Eye, EyeOff } from 'lucide-react';
import type { Config } from '../lib/api';

interface ConfigEditorProps {
  config: Config;
  onSave: (config: Partial<Config>) => Promise<void>;
}

export const ConfigEditor: React.FC<ConfigEditorProps> = ({ config, onSave }) => {
  const [showKey, setShowKey] = useState(false);
  const [formData, setFormData] = useState<Partial<Config>>(config);
  const [saving, setSaving] = useState(false);

  const handleSave = async () => {
    setSaving(true);
    try {
      await onSave(formData);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Azure Configuration */}
      <motion.div
        className="swag-card"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <h3 className="text-xl font-bold text-swag-neon-blue mb-4">
          🔷 Azure Form Recognizer
        </h3>
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-semibold mb-2">Endpoint</label>
            <input
              type="text"
              className="swag-input w-full"
              value={formData.azure?.endpoint || ''}
              onChange={(e) =>
                setFormData({
                  ...formData,
                  azure: { ...formData.azure, endpoint: e.target.value, key: formData.azure?.key || '' },
                })
              }
              placeholder="https://your-resource.cognitiveservices.azure.com/"
            />
          </div>
          <div>
            <label className="block text-sm font-semibold mb-2">API Key</label>
            <div className="relative">
              <input
                type={showKey ? 'text' : 'password'}
                className="swag-input w-full pr-12"
                value={formData.azure?.key || ''}
                onChange={(e) =>
                  setFormData({
                    ...formData,
                    azure: { ...formData.azure, key: e.target.value, endpoint: formData.azure?.endpoint || '' },
                  })
                }
                placeholder="Enter API key"
              />
              <button
                onClick={() => setShowKey(!showKey)}
                className="absolute right-3 top-1/2 transform -translate-y-1/2 text-swag-neon-green hover:text-swag-neon-blue"
              >
                {showKey ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
              </button>
            </div>
          </div>
        </div>
      </motion.div>

      {/* Google Sheets Configuration */}
      <motion.div
        className="swag-card"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
      >
        <h3 className="text-xl font-bold text-swag-neon-green mb-4">
          📊 Google Sheets
        </h3>
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-semibold mb-2">Sheet ID</label>
            <input
              type="text"
              className="swag-input w-full"
              value={formData.google_sheets?.sheet_id || ''}
              onChange={(e) =>
                setFormData({
                  ...formData,
                  google_sheets: { ...formData.google_sheets!, sheet_id: e.target.value },
                })
              }
            />
          </div>
          <div>
            <label className="block text-sm font-semibold mb-2">Sheet Name</label>
            <input
              type="text"
              className="swag-input w-full"
              value={formData.google_sheets?.sheet_name || ''}
              onChange={(e) =>
                setFormData({
                  ...formData,
                  google_sheets: { ...formData.google_sheets!, sheet_name: e.target.value },
                })
              }
            />
          </div>
        </div>
      </motion.div>

      {/* Variance Thresholds */}
      <motion.div
        className="swag-card"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
      >
        <h3 className="text-xl font-bold text-swag-gold mb-4">
          🚦 Variance Thresholds
        </h3>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-semibold mb-2">Green (%)</label>
            <input
              type="number"
              className="swag-input w-full"
              value={formData.variance_thresholds?.green || 3}
              onChange={(e) =>
                setFormData({
                  ...formData,
                  variance_thresholds: {
                    ...formData.variance_thresholds!,
                    green: parseFloat(e.target.value),
                  },
                })
              }
              step="0.5"
              min="0"
            />
          </div>
          <div>
            <label className="block text-sm font-semibold mb-2">Yellow (%)</label>
            <input
              type="number"
              className="swag-input w-full"
              value={formData.variance_thresholds?.yellow || 10}
              onChange={(e) =>
                setFormData({
                  ...formData,
                  variance_thresholds: {
                    ...formData.variance_thresholds!,
                    yellow: parseFloat(e.target.value),
                  },
                })
              }
              step="0.5"
              min="0"
            />
          </div>
        </div>
      </motion.div>

      {/* Save Button */}
      <motion.button
        className="swag-btn w-full flex items-center justify-center gap-2"
        onClick={handleSave}
        disabled={saving}
        whileHover={{ scale: 1.02 }}
        whileTap={{ scale: 0.98 }}
      >
        <Save className="w-5 h-5" />
        {saving ? 'Saving...' : '💾 Save Configuration'}
      </motion.button>
    </div>
  );
};
```

### 4. Page Components

#### 4.1 Dashboard Page

**File**: `/frontend/src/pages/Dashboard.tsx`

```typescript
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
```

#### 4.2 Upload Page

**File**: `/frontend/src/pages/Upload.tsx`

```typescript
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
    refetchInterval: (data) => {
      // Stop refetching when job is complete or failed
      if (data?.status === 'completed' || data?.status === 'failed') {
        return false;
      }
      return 2000; // Poll every 2 seconds
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
```

#### 4.3 Settings Page

**File**: `/frontend/src/pages/Settings.tsx`

```typescript
import React from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { getConfig, updateConfig } from '../lib/api';
import { ConfigEditor } from '../components/ConfigEditor';
import { motion } from 'framer-motion';
import { toast } from 'react-hot-toast';

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
```

#### 4.4 History Page

**File**: `/frontend/src/pages/History.tsx`

```typescript
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
                    {new Date(file.modified).toLocaleString()}
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
```

### 5. Main App Structure

#### 5.1 App Router

**File**: `/frontend/src/App.tsx`

```typescript
import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Toaster } from 'react-hot-toast';
import { Sidebar } from './components/Sidebar';
import { Dashboard } from './pages/Dashboard';
import { Upload } from './pages/Upload';
import { Settings } from './pages/Settings';
import { History } from './pages/History';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <div className="flex min-h-screen bg-swag-dark">
          <Sidebar />
          <main className="flex-1 ml-64 p-8">
            <Routes>
              <Route path="/" element={<Navigate to="/dashboard" replace />} />
              <Route path="/dashboard" element={<Dashboard />} />
              <Route path="/upload" element={<Upload />} />
              <Route path="/settings" element={<Settings />} />
              <Route path="/history" element={<History />} />
            </Routes>
          </main>
        </div>
        <Toaster
          position="top-right"
          toastOptions={{
            duration: 4000,
            style: {
              background: '#1C1C1C',
              color: '#F8F8F8',
              border: '2px solid #32FF6A',
            },
          }}
        />
      </BrowserRouter>
    </QueryClientProvider>
  );
}

export default App;
```

#### 5.2 Sidebar Component

**File**: `/frontend/src/components/Sidebar.tsx`

```typescript
import React from 'react';
import { NavLink } from 'react-router-dom';
import { LayoutDashboard, Upload, Settings, History, Zap } from 'lucide-react';
import { motion } from 'framer-motion';

export const Sidebar: React.FC = () => {
  const links = [
    { to: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { to: '/upload', label: 'Upload & Process', icon: Upload },
    { to: '/history', label: 'History', icon: History },
    { to: '/settings', label: 'Settings', icon: Settings },
  ];

  return (
    <div className="sidebar">
      {/* Logo */}
      <motion.div
        className="mb-8"
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <div className="flex items-center gap-3">
          <Zap className="w-10 h-10 text-swag-neon-green" />
          <div>
            <h1 className="text-xl font-black text-transparent bg-gradient-to-r from-swag-neon-green to-swag-neon-blue bg-clip-text">
              SWAG PRICING
            </h1>
            <p className="text-xs text-swag-gold">INTELLIGENCE TOOL</p>
          </div>
        </div>
      </motion.div>

      {/* Navigation Links */}
      <nav className="space-y-2">
        {links.map((link, index) => {
          const Icon = link.icon;
          return (
            <motion.div
              key={link.to}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.1 }}
            >
              <NavLink
                to={link.to}
                className={({ isActive }) =>
                  `sidebar-link ${isActive ? 'sidebar-link-active' : ''}`
                }
              >
                <Icon className="w-5 h-5" />
                <span className="font-semibold">{link.label}</span>
              </NavLink>
            </motion.div>
          );
        })}
      </nav>

      {/* Footer */}
      <div className="mt-auto pt-6 border-t border-swag-neon-green/20">
        <p className="text-xs text-swag-skull-white/50 text-center">
          v2.0.0 • LOCAL DEPLOY
        </p>
        <p className="text-xs text-swag-gold/70 text-center mt-1">
          PHASE 5: REACT MIGRATION
        </p>
      </div>
    </div>
  );
};
```

---

## 📦 Installation & Setup

### Backend Setup

```bash
# Install backend dependencies
cd /Users/ryanwatson/Desktop/SwagInvoice
pip install -r backend/requirements.txt

# Start FastAPI server
cd backend
uvicorn main:app --reload --port 8000
```

### Frontend Setup

```bash
# Install frontend dependencies (already done)
cd /Users/ryanwatson/Desktop/SwagInvoice/frontend
npm install

# Install additional dependency
npm install react-hot-toast

# Create .env file
echo "VITE_API_URL=http://localhost:8000" > .env

# Start development server
npm run dev
```

---

## 🚀 Running the Application

### Development Mode

**Terminal 1** (Backend):
```bash
cd /Users/ryanwatson/Desktop/SwagInvoice/backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2** (Frontend):
```bash
cd /Users/ryanwatson/Desktop/SwagInvoice/frontend
npm run dev
```

**Access**:
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Production Build

```bash
# Build frontend
cd /Users/ryanwatson/Desktop/SwagInvoice/frontend
npm run build

# Serve via FastAPI (uncomment app.mount in backend/main.py)
cd /Users/ryanwatson/Desktop/SwagInvoice/backend
uvicorn main:app --host 0.0.0.0 --port 8000
```

---

## 🎨 Design System Reference

### Colors
- **Primary Dark**: `#0F0F0F` - Base background
- **Secondary Dark**: `#1C1C1C` - Cards/containers
- **Tertiary Dark**: `#2A2A2A` - Hover states
- **Neon Green**: `#32FF6A` - Primary accent
- **Neon Blue**: `#00BFFF` - Secondary accent
- **Gold**: `#D4AF37` - Tertiary accent
- **White**: `#F8F8F8` - Text

### Typography
- **Display**: Orbitron (headers, logos)
- **Body**: Inter (content)

### Components
- `.swag-card` - Container with gradient and border
- `.swag-btn` - Primary CTA button
- `.swag-btn-secondary` - Secondary button
- `.upload-zone` - Drag-and-drop area
- `.stat-card` - Dashboard metric card
- `.swag-input` - Form input field

---

## 🔜 Next Steps

1. **Complete Component Implementation** - Copy component code from this document
2. **Install Missing Dependencies**: `npm install react-hot-toast`
3. **Create Environment File**: `.env` with `VITE_API_URL=http://localhost:8000`
4. **Test API Integration** - Verify all endpoints work
5. **Add Toast Notifications** - User feedback for actions
6. **Implement Framer Motion Animations** - Polish interactions
7. **Electron Packaging** (Future Phase 6)

---

## ✅ Success Criteria

- [x] FastAPI backend with all endpoints
- [x] React + TypeScript + Vite setup
- [x] Tailwind CSS with Swag Golf theme
- [x] API client with TypeScript types
- [ ] All React components implemented
- [ ] All pages functional
- [ ] CORS configured and tested
- [ ] End-to-end workflow tested
- [ ] Production build ready

---

**Status**: 60% Complete
**Next Priority**: Implement remaining React components and pages
