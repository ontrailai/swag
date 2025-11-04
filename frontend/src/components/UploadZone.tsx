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
        onClick={() => !disabled && inputRef.current?.click()}
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
