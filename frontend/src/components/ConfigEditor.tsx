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
