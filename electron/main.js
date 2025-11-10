const { app, BrowserWindow, screen, dialog } = require('electron');
const { spawn } = require('child_process');
const path = require('path');
const waitOn = require('wait-on');
const http = require('http');
const fs = require('fs');

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

// Check if Python is installed
function checkPythonInstalled(pythonCmd) {
  return new Promise((resolve) => {
    const testProcess = spawn(pythonCmd, ['--version'], {
      stdio: 'pipe',
      shell: true
    });

    let output = '';
    testProcess.stdout.on('data', (data) => {
      output += data.toString();
    });

    testProcess.stderr.on('data', (data) => {
      output += data.toString();
    });

    testProcess.on('close', (code) => {
      console.log('Python check output:', output);
      resolve(code === 0 && output.toLowerCase().includes('python'));
    });

    testProcess.on('error', () => {
      resolve(false);
    });

    // Timeout after 5 seconds
    setTimeout(() => {
      testProcess.kill();
      resolve(false);
    }, 5000);
  });
}

// Show error dialog to user
function showErrorDialog(title, message) {
  dialog.showErrorBox(title, message);
}

// Set up user data directory with config files
function setupDataDirectory() {
  console.log('Setting up data directory...');

  // Get user data path
  const userDataPath = app.getPath('userData');
  console.log('User data path:', userDataPath);

  // Create userData directory if it doesn't exist
  if (!fs.existsSync(userDataPath)) {
    fs.mkdirSync(userDataPath, { recursive: true });
  }

  // Only copy files if running packaged version
  if (app.isPackaged) {
    const resourcesPath = process.resourcesPath;

    // Copy config files if they don't exist
    const filesToCopy = ['config.json', 'credentials.json', 'token.json'];
    filesToCopy.forEach(file => {
      const source = path.join(resourcesPath, file);
      const dest = path.join(userDataPath, file);

      if (fs.existsSync(source) && !fs.existsSync(dest)) {
        console.log(`Copying ${file} to user data directory`);
        fs.copyFileSync(source, dest);
      }
    });

    // Create Invoices directory structure
    const invoicesPath = path.join(userDataPath, 'Invoices');
    const invoicesNew = path.join(invoicesPath, 'new');
    const invoicesProcessed = path.join(invoicesPath, 'processed');

    if (!fs.existsSync(invoicesNew)) {
      fs.mkdirSync(invoicesNew, { recursive: true });
      console.log('Created Invoices/new directory');
    }

    if (!fs.existsSync(invoicesProcessed)) {
      fs.mkdirSync(invoicesProcessed, { recursive: true });
      console.log('Created Invoices/processed directory');
    }

    // Copy existing invoices if available
    const sourceInvoices = path.join(resourcesPath, 'Invoices');
    if (fs.existsSync(sourceInvoices) && fs.existsSync(invoicesPath)) {
      // Copy processed invoices
      const sourceProcessed = path.join(sourceInvoices, 'processed');
      if (fs.existsSync(sourceProcessed)) {
        const files = fs.readdirSync(sourceProcessed);
        files.forEach(file => {
          const src = path.join(sourceProcessed, file);
          const dst = path.join(invoicesProcessed, file);
          if (!fs.existsSync(dst) && fs.statSync(src).isFile()) {
            fs.copyFileSync(src, dst);
          }
        });
        console.log(`Copied ${files.length} processed invoices`);
      }
    }
  }

  return userDataPath;
}

// Start FastAPI backend
async function startBackend() {
  return new Promise(async (resolve, reject) => {
    console.log('Starting FastAPI backend...');

    // Determine project root - different for packaged vs development
    const projectRoot = app.isPackaged
      ? path.join(process.resourcesPath, 'app')
      : path.join(__dirname, '..');

    // For packaged app, use userData as working directory
    const workingDir = app.isPackaged ? app.getPath('userData') : projectRoot;

    console.log('Project root:', projectRoot);
    console.log('Working directory:', workingDir);

    // Determine Python path based on platform
    let pythonPath;
    if (process.platform === 'win32') {
      // On Windows, try common Python locations
      pythonPath = 'python'; // Will use system PATH
    } else if (process.platform === 'darwin') {
      // On macOS
      pythonPath = '/Users/ryanwatson/.pyenv/shims/python3';
    } else {
      // On Linux
      pythonPath = 'python3';
    }

    // Check if Python is installed
    console.log('Checking Python installation...');
    const pythonInstalled = await checkPythonInstalled(pythonPath);
    if (!pythonInstalled) {
      const errorMsg = `Python is not installed or not found in system PATH.\n\n` +
        `Please install Python 3.8 or newer from:\nhttps://www.python.org/downloads/\n\n` +
        `Make sure to check "Add Python to PATH" during installation.`;
      showErrorDialog('Python Not Found', errorMsg);
      reject(new Error('Python not installed'));
      return;
    }
    console.log('Python found!');

    // Create log file for debugging
    const logPath = path.join(workingDir, 'backend-startup.log');
    const logStream = fs.createWriteStream(logPath, { flags: 'w' });
    console.log('Log file:', logPath);

    // Set PYTHONPATH to include project root modules
    const env = { ...process.env };
    const pathSep = process.platform === 'win32' ? ';' : ':';

    // Force UTF-8 encoding on Windows
    if (process.platform === 'win32') {
      env.PYTHONIOENCODING = 'utf-8';
      env.PYTHONUTF8 = '1';
    }

    if (app.isPackaged) {
      // For packaged app, add both project root and src to PYTHONPATH
      const pythonPaths = [projectRoot, path.join(projectRoot, 'src')];
      env.PYTHONPATH = pythonPaths.join(pathSep) + (env.PYTHONPATH ? pathSep + env.PYTHONPATH : '');
    } else {
      env.PYTHONPATH = projectRoot;
    }

    // Create a startup script file to avoid command-line escaping issues
    let uvicornArgs;
    let startupScriptPath;

    if (app.isPackaged) {
      // Write Python startup script to temp file
      startupScriptPath = path.join(workingDir, 'start_backend.py');
      const startupScript = `# -*- coding: utf-8 -*-
import sys
import os

# Force UTF-8 encoding on Windows - MUST be done before any imports
if sys.platform == 'win32':
    import io
    # Reconfigure stdout and stderr with UTF-8 encoding and error handling
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace', line_buffering=True)

# Add paths to Python path
sys.path.insert(0, r'${projectRoot}')
sys.path.insert(0, r'${path.join(projectRoot, 'src')}')

# Change to working directory
os.chdir(r'${workingDir}')

# Start uvicorn
from uvicorn import run
run('backend.main:app', host='0.0.0.0', port=${BACKEND_PORT})
`;

      fs.writeFileSync(startupScriptPath, startupScript, 'utf8');
      console.log('Created startup script:', startupScriptPath);
      logStream.write(`Created startup script: ${startupScriptPath}\n`);

      // Simple direct approach - no shell, just pass path as argument
      uvicornArgs = [startupScriptPath];
    } else {
      uvicornArgs = [
        '-m', 'uvicorn',
        'backend.main:app',
        '--host', '0.0.0.0',
        '--port', BACKEND_PORT.toString()
      ];
    }

    console.log('Starting backend with command:', pythonPath, uvicornArgs);
    logStream.write(`Starting backend...\n`);
    logStream.write(`Python: ${pythonPath}\n`);
    logStream.write(`Project root: ${projectRoot}\n`);
    logStream.write(`Working dir: ${workingDir}\n`);
    logStream.write(`Command: ${pythonPath} ${JSON.stringify(uvicornArgs)}\n\n`);

    backendProcess = spawn(pythonPath, uvicornArgs, {
      cwd: app.isPackaged ? projectRoot : workingDir,
      stdio: ['ignore', 'pipe', 'pipe'],
      env: env
      // NO shell - Node.js handles paths with spaces correctly without it
    });

    backendProcess.stdout.on('data', (data) => {
      const msg = data.toString();
      console.log(`Backend: ${msg}`);
      logStream.write(`STDOUT: ${msg}\n`);
    });

    backendProcess.stderr.on('data', (data) => {
      const msg = data.toString();
      console.error(`Backend Error: ${msg}`);
      logStream.write(`STDERR: ${msg}\n`);
    });

    backendProcess.on('error', (error) => {
      console.error('Failed to start backend:', error);
      logStream.write(`ERROR: ${error.message}\n`);
      logStream.end();

      showErrorDialog(
        'Backend Startup Failed',
        `Failed to start the application backend.\n\n` +
        `Error: ${error.message}\n\n` +
        `Check the log file at:\n${logPath}`
      );
      reject(error);
    });

    backendProcess.on('exit', (code, signal) => {
      logStream.write(`Process exited with code ${code}, signal ${signal}\n`);
      logStream.end();
    });

    // Wait for backend to be ready
    let attempts = 0;
    const maxAttempts = 60; // 30 seconds (60 * 500ms)

    const checkInterval = setInterval(async () => {
      attempts++;
      const isReady = await checkBackendHealth();
      if (isReady) {
        clearInterval(checkInterval);
        console.log('Backend is ready!');
        logStream.write('Backend is ready!\n');
        logStream.end();
        resolve();
      } else if (attempts >= maxAttempts) {
        clearInterval(checkInterval);
        logStream.write('Backend startup timeout\n');
        logStream.end();

        showErrorDialog(
          'Backend Startup Timeout',
          `The application backend failed to start within 30 seconds.\n\n` +
          `This may be due to:\n` +
          `- Missing Python packages (pip install fastapi uvicorn)\n` +
          `- Port 8000 already in use\n` +
          `- Firewall blocking the connection\n\n` +
          `Check the log file at:\n${logPath}`
        );
        reject(new Error('Backend startup timeout'));
      }
    }, 500);
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

    // Set up data directory (copies config files for packaged app)
    setupDataDirectory();

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
