const { app, BrowserWindow, screen } = require('electron');
const { spawn } = require('child_process');
const path = require('path');
const waitOn = require('wait-on');
const http = require('http');

// Set app name
app.name = "Swag Pricing Intelligence";

let mainWindow;
let splashWindow;
let backendProcess;
const BACKEND_PORT = 8000;
const BACKEND_URL = `http://localhost:${BACKEND_PORT}`;

// Disable hardware acceleration for better compatibility
app.disableHardwareAcceleration();

// Check if backend is ready
function checkBackendHealth() {
  return new Promise((resolve) => {
    const req = http.get(`${BACKEND_URL}/health`, (res) => {
      resolve(res.statusCode === 200);
    });
    req.on('error', () => resolve(false));
    req.setTimeout(1000, () => {
      req.destroy();
      resolve(false);
    });
  });
}

// Start FastAPI backend
async function startBackend() {
  return new Promise((resolve, reject) => {
    console.log('Starting FastAPI backend...');

    const projectRoot = path.join(__dirname, '..');
    const pythonPath = process.platform === 'win32' ? 'python' : 'python3';

    backendProcess = spawn(pythonPath, [
      '-m', 'uvicorn',
      'backend.main:app',
      '--host', '0.0.0.0',
      '--port', BACKEND_PORT.toString()
    ], {
      cwd: projectRoot,
      stdio: ['ignore', 'pipe', 'pipe']
    });

    backendProcess.stdout.on('data', (data) => {
      console.log(`Backend: ${data}`);
    });

    backendProcess.stderr.on('data', (data) => {
      console.error(`Backend Error: ${data}`);
    });

    backendProcess.on('error', (error) => {
      console.error('Failed to start backend:', error);
      reject(error);
    });

    // Wait for backend to be ready
    const checkInterval = setInterval(async () => {
      const isReady = await checkBackendHealth();
      if (isReady) {
        clearInterval(checkInterval);
        console.log('Backend is ready!');
        resolve();
      }
    }, 500);

    // Timeout after 30 seconds
    setTimeout(() => {
      clearInterval(checkInterval);
      reject(new Error('Backend startup timeout'));
    }, 30000);
  });
}

// Create splash screen
function createSplashScreen() {
  const { width, height } = screen.getPrimaryDisplay().workAreaSize;

  splashWindow = new BrowserWindow({
    width: 800,
    height: 400,
    frame: false,
    transparent: true,
    alwaysOnTop: true,
    center: true,
    resizable: false,
    backgroundColor: '#0F0F0F',
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true
    }
  });

  // Load splash HTML
  splashWindow.loadURL(`data:text/html;charset=utf-8,${encodeURIComponent(`
    <!DOCTYPE html>
    <html>
      <head>
        <style>
          body {
            margin: 0;
            padding: 0;
            background: #0F0F0F;
            display: flex;
            align-items: center;
            justify-content: center;
            height: 100vh;
            font-family: 'Orbitron', sans-serif;
            overflow: hidden;
          }
          .splash-container {
            text-align: center;
          }
          .logo {
            width: 150px;
            height: 150px;
            margin: 0 auto 30px;
            animation: pulse 2s ease-in-out infinite;
          }
          .title {
            font-size: 32px;
            font-weight: 900;
            background: linear-gradient(90deg, #32FF6A, #00BFFF, #D4AF37);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 10px;
            letter-spacing: 4px;
          }
          .subtitle {
            font-size: 16px;
            color: rgba(248, 248, 248, 0.7);
            letter-spacing: 2px;
          }
          .loader {
            display: flex;
            justify-content: center;
            gap: 10px;
            margin-top: 30px;
          }
          .dot {
            width: 12px;
            height: 12px;
            background: #32FF6A;
            border-radius: 50%;
            animation: bounce 1.4s infinite ease-in-out both;
          }
          .dot:nth-child(1) { animation-delay: -0.32s; }
          .dot:nth-child(2) { animation-delay: -0.16s; }
          @keyframes pulse {
            0%, 100% { transform: scale(1); filter: drop-shadow(0 0 20px rgba(50, 255, 106, 0.6)); }
            50% { transform: scale(1.05); filter: drop-shadow(0 0 30px rgba(255, 60, 241, 0.8)); }
          }
          @keyframes bounce {
            0%, 80%, 100% { transform: scale(0); }
            40% { transform: scale(1); }
          }
        </style>
      </head>
      <body>
        <div class="splash-container">
          <div class="logo">
            <svg viewBox="0 0 200 200" fill="none" xmlns="http://www.w3.org/2000/svg">
              <defs>
                <linearGradient id="swagGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" style="stop-color:#32FF6A;stop-opacity:1" />
                  <stop offset="100%" style="stop-color:#FF3CF1;stop-opacity:1" />
                </linearGradient>
              </defs>
              <ellipse cx="100" cy="110" rx="60" ry="70" fill="#0F0F0F" stroke="url(#swagGradient)" stroke-width="3"/>
              <ellipse cx="80" cy="95" rx="12" ry="18" fill="#32FF6A" opacity="0.9"/>
              <ellipse cx="120" cy="95" rx="12" ry="18" fill="#32FF6A" opacity="0.9"/>
              <path d="M 95 115 L 100 125 L 105 115 Z" fill="#32FF6A" opacity="0.8"/>
              <rect x="70" y="140" width="12" height="18" rx="2" fill="#F8F8F8"/>
              <rect x="85" y="140" width="12" height="18" rx="2" fill="#F8F8F8"/>
              <rect x="103" y="140" width="12" height="18" rx="2" fill="#F8F8F8"/>
              <rect x="118" y="140" width="12" height="18" rx="2" fill="#F8F8F8"/>
              <text x="100" y="30" font-family="Orbitron" font-size="24" font-weight="900" fill="url(#swagGradient)" text-anchor="middle" letter-spacing="4">SWAG</text>
            </svg>
          </div>
          <div class="title">SWAG GOLF</div>
          <div class="subtitle">Pricing Intelligence</div>
          <div class="loader">
            <div class="dot"></div>
            <div class="dot"></div>
            <div class="dot"></div>
          </div>
        </div>
      </body>
    </html>
  `)}`);
}

// Create main window
function createMainWindow() {
  const { width, height } = screen.getPrimaryDisplay().workAreaSize;

  mainWindow = new BrowserWindow({
    width: 1400,
    height: 900,
    minWidth: 1024,
    minHeight: 768,
    title: 'Swag Pricing Intelligence',
    show: false,
    center: true,
    backgroundColor: '#0F0F0F',
    autoHideMenuBar: true,
    titleBarStyle: 'hiddenInset',
    icon: path.join(__dirname, 'icon.png'),
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      nodeIntegration: false,
      contextIsolation: true,
      devTools: false
    }
  });

  // Load the app
  mainWindow.loadURL(BACKEND_URL);

  // Show window when ready
  mainWindow.once('ready-to-show', () => {
    setTimeout(() => {
      if (splashWindow) {
        splashWindow.close();
        splashWindow = null;
      }
      mainWindow.show();
      mainWindow.focus();
    }, 2000);
  });

  // Handle window close
  mainWindow.on('closed', () => {
    mainWindow = null;
  });

  // Prevent navigation to external URLs
  mainWindow.webContents.on('will-navigate', (event, url) => {
    if (!url.startsWith(BACKEND_URL)) {
      event.preventDefault();
    }
  });

  // Prevent new windows
  mainWindow.webContents.setWindowOpenHandler(() => {
    return { action: 'deny' };
  });
}

// App initialization
app.whenReady().then(async () => {
  try {
    // Set About panel options (macOS)
    app.setAboutPanelOptions({
      applicationName: "Swag Pricing Intelligence",
      applicationVersion: "1.0.0",
      credits: "Developed for Swag Golf by Ryan Watson",
      iconPath: path.join(__dirname, 'icon.png')
    });

    // Show splash screen
    createSplashScreen();

    // Start backend
    await startBackend();

    // Create main window
    createMainWindow();
  } catch (error) {
    console.error('Failed to initialize app:', error);
    app.quit();
  }
});

// Quit when all windows are closed
app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

// macOS activate
app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) {
    createMainWindow();
  }
});

// Clean up on quit
app.on('will-quit', () => {
  if (backendProcess) {
    console.log('Shutting down backend...');
    backendProcess.kill('SIGTERM');

    // Force kill after 5 seconds
    setTimeout(() => {
      if (backendProcess) {
        backendProcess.kill('SIGKILL');
      }
    }, 5000);
  }
});

// Handle uncaught exceptions
process.on('uncaughtException', (error) => {
  console.error('Uncaught exception:', error);
});
