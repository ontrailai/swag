const { contextBridge, ipcRenderer } = require('electron');

// Expose protected methods that allow the renderer process to use
// ipcRenderer without exposing the entire object
contextBridge.exposeInMainWorld('electronAPI', {
  // App information
  getVersion: () => ipcRenderer.invoke('app:get-version'),

  // Backend status
  checkBackendStatus: () => ipcRenderer.invoke('backend:check-status'),

  // Window controls
  minimizeWindow: () => ipcRenderer.send('window:minimize'),
  maximizeWindow: () => ipcRenderer.send('window:maximize'),
  closeWindow: () => ipcRenderer.send('window:close'),

  // File operations
  selectFile: () => ipcRenderer.invoke('dialog:select-file'),
  selectFolder: () => ipcRenderer.invoke('dialog:select-folder'),

  // Notifications
  showNotification: (title, body) => ipcRenderer.send('notification:show', { title, body }),

  // Event listeners
  onBackendStatusChange: (callback) => ipcRenderer.on('backend:status-changed', callback),
  removeBackendStatusListener: () => ipcRenderer.removeAllListeners('backend:status-changed')
});

// Log when preload script is loaded
console.log('Preload script loaded successfully');
