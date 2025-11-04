import React, { useState, useRef } from 'react';
import { Upload, FileText, X } from 'lucide-react';
import { motion } from 'framer-motion';
import swagLogo from '../assets/swag-logo.svg';

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
        className={`upload-zone relative overflow-hidden ${dragActive ? 'border-swag-neon-green shadow-neon-green' : ''} ${
          disabled ? 'opacity-50 cursor-not-allowed' : ''
        }`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
        onClick={() => !disabled && inputRef.current?.click()}
        whileHover={!disabled ? { scale: 1.02 } : {}}
        whileTap={!disabled ? { scale: 0.98 } : {}}
      >
        {/* Background logo watermark */}
        <div className="absolute inset-0 flex items-center justify-center opacity-5">
          <img src={swagLogo} alt="" className="w-64 h-64" />
        </div>

        <div className="relative z-10">
          <motion.div
            animate={dragActive ? {
              scale: [1, 1.1, 1],
              rotate: [0, 5, -5, 0]
            } : {}}
            transition={{ duration: 0.5 }}
          >
            <Upload className="w-16 h-16 mx-auto mb-4 text-swag-neon-green drop-shadow-lg" />
          </motion.div>

          <h3 className="text-2xl font-display font-bold uppercase tracking-wider text-swag-skull-white mb-2">
            Drop Invoice PDFs
          </h3>

          <p className="text-swag-skull-white/70 mb-4 font-body">
            or click to browse files
          </p>

          <div className="flex items-center justify-center gap-2 text-sm text-swag-gold">
            <div className="w-12 h-px bg-gradient-to-r from-transparent via-swag-gold to-transparent" />
            <span className="font-semibold">Multiple files supported</span>
            <div className="w-12 h-px bg-gradient-to-r from-transparent via-swag-gold to-transparent" />
          </div>
        </div>

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
